import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from db_wrapper import DbWrapper
from get_graphs import get_graphs
from utils import get_account_text

# Plotly如果要在線上server的網頁顯示(不是本機host)，是須要提供一個api_key才能夠使用，但在自已電腦為host的話，就可以不用提供
# chart_studio.tools.set_credentials_file(username='', api_key='')

# stylesheets 就是CSS的檔案，以下是使用連線的方式去拿到CSS檔
external_stylesheets = ["https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css",
                        "https://cdn.rawgit.com/yclliu/dash-css/37c322c/main.css"]

db_wrapper = DbWrapper()  # 作成DbWrapper()實例，連線到資料庫

app = dash.Dash('Live Air Quality', external_stylesheets=external_stylesheets)  # 建立dash的app
server = app.server
app.title = 'Pi-Air'  # 設定title

# 網頁顯示的架構，圖面顯示
content = [
    # Sensor有沒有在線上(執行中)
    html.Div([
        html.Div(id='accounts-status-text', className=''),
    ], className='row accounts-status'),

    # 大圖表的的命名為「main-graphs」
    html.Div(children=html.Div(id='main-graphs'), className='row'),
    # Interval的功能是可以每固定時間來更新一次；Interval就是時間窗格
    # interval=30 * 1000 意為每30秒更新一次
    dcc.Interval(id='interval-component-main', interval=30 * 1000, n_intervals=0),

    # 小圖表命名為「graphs」
    html.Div(children=html.Div(id='graphs'), className='row'),
    # interval=3 * 1000 意為每3秒更新一次
    dcc.Interval(id='interval-component', interval=3 * 1000, n_intervals=0),

    # 網頁結尾的部份(Footer)
    html.Footer(html.Div(html.Div(
        html.Div(html.Span('Python-Advanced Course Pi-Air Project'), className='col-sm-8 col-sm-offset-2 text-center'),
        className='row'), className='container'), className='footer-padding')
]

# 設計dash的layout
# 網頁的排版設計；Div是網頁裡的區塊
# H2是標題的意思，navbar(navigation bar)，而裡面的className的定意來自external_stylesheets的CSS檔
# 而最後的一個Div，裡面的內容太多了，另外寫在別的地方
app.layout = html.Div([
    html.Div([html.H2('Chien_Pi-Air')], className='navbar navbar-default navbar-fixed-top'),
    html.Div(content, className="container")
])


@app.callback(Output('accounts-status-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_accounts_status(n_intervals):
    class_choice = 'col-xs-12 col-sm-6 col-md-6 col-lg-6'
    sensor_online = db_wrapper.is_online()
    status_text_1, status_class_name_1 = get_account_text(sensor_online)

    return html.Div([
        html.Span('在線狀態： Sensor: '),
        html.Span(status_text_1),
        html.Span('', className=status_class_name_1)
    ], className=class_choice)


# 更新大圖表
# 這個為callback function，因某些事件被觸發的後才會被執行的function
# 在這個decorator裡的Input的東西，會觸發function執行
# 而Output就是輸出的資料，而這些輸出的資料被已被function加工了
# get_graphs()是處理圖表的function
@app.callback(
    Output('main-graphs', 'children'),
    [Input('interval-component-main', 'n_intervals')])
def update_main_graphs(n_intervals):
    # is_main_graphs=True為傳資料給大圖，預設為False
    # 因為圖表是要跟資料庫拿資料，所以也將db_wrapper投進來
    return get_graphs(db_wrapper, is_main_graphs=True)


# 更新小圖表
@app.callback(
    Output('graphs', 'children'),
    [Input('interval-component', 'n_intervals')])
def update_graphs(n_intervals):
    return get_graphs(db_wrapper, is_main_graphs=False)


if __name__ == '__main__':
    app.run_server(debug=True)
