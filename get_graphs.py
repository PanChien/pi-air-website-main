import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from utils import utc_to_local, format_title

LINE_COLOR = "#27b5b3"  # 圖表線的顏色
SOURCES = ['VOC-CCS', 'VOC-TGS', 'PM25', 'PM10']  # 資料庫的4種數值


def get_graphs(db_wrapper, is_main_graphs=False):
    graphs = []
    if is_main_graphs:  # 大圖，大圖跟小圖的差別只有CSS的不同
        # s12 大圖佔12等份(不管視窗大小)
        class_names = 'graph-div col s12'  # 這個排版方式使用CSS的Bootstrap Grid System(會依照視窗大小來調整)
        data = db_wrapper.get_data(limit=300)  # minute=True
    else:  # small graphs
        # col-xs-12 視窗畫面很小時，就使用12等份，xs
        # col-sm-6、col-md-6、col-lg-6 小、中、大的視窗，就給6等份大小
        class_names = 'graph-div col-xs-12 col-sm-6 col-md-6 col-lg-6'
        data = db_wrapper.get_data(limit=300)  # 投入limit=180，為180筆資料

    # 真正劃成圖表的程式部份
    for source in SOURCES:
        x = [utc_to_local(d['at']) for d in data]  # 圖表軸，時間
        y = [float(d[source]) for d in data]  # 圖表Y軸，sensor的值

        # 使用Plotly裡的Scatter的圖
        # 圖表上的點或線，被稱為trace
        trace = go.Scatter(
            x=x,
            y=y,
            mode='lines',
            line=dict(color=LINE_COLOR, width=3),
        )

        # layout是關於圖表的樣貌
        layout = get_layout(x, y)

        # dash_core_components裡的物件「Graph」
        dcc_graph = dcc.Graph(
            id=source,
            figure={'data': [trace], 'layout': layout},
            config={'displayModeBar': False}
        )

        # title 圖表的標題
        source_title = source
        if source == 'PM25':
            source_title = 'PM2.5'
        title = format_title(source_title, y[0]) if y else 'no data'  # 加上單位

        # output div
        # 把標題跟圖表結合在一起
        graph_div = html.Div([
            html.Div([
                html.H3(title)
            ], className='Title'),
            dcc_graph,
        ], className=class_names)

        graphs.append(graph_div)

    return graphs


# 圖表樣貌的function，可以去Plotly來學習使用
def get_layout(x, y):
    min_x = min(x) if x else 0
    max_x = max(x) if x else 0
    min_y = min(y) if y else 0
    max_y = max(y) if y else 0

    return go.Layout(
        xaxis=dict(
            range=[min_x, max_x],
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickcolor='rgb(204, 204, 204)',
            tickwidth=2,
            ticklen=5,
            tickfont=dict(
                size=12,
                color='rgb(204, 204, 204)',
            )
        ),
        yaxis=dict(
            range=[min_y, max_y],
            tickcolor='rgb(204, 204, 204)',
            showgrid=False,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,

            hoverformat='.0f',
            tickfont=dict(
                size=12,
                color='rgb(204, 204, 204)',
            )
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=370,
        margin=go.layout.Margin(
            t=30,
            l=55,
            r=20,
            b=70
        ),
        hoverlabel=dict(
            bgcolor='#FFA200',
        )
    )
