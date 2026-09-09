import dash
from dash import dcc, html, Input, Output, State
import os
import sys
folders = ['Utilities', 'Ecosystem', 'Backtester', 'Analysis']
for folder in folders:
    path_to_folders = os.path.join('C:\\Users\\' + os.getlogin() +'\\Source\\Repos\\Investments-Quant\\' + folder)
    if path_to_folders not in sys.path:
        print(path_to_folders)
        sys.path.append(path_to_folders)
#import Live_Dash  # import your Live_dash app
import web_trial

app = dash.Dash(__name__, suppress_callback_exceptions=True)#, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='current-pathname', storage_type='session'),
    html.Div(id='page-content'),
    html.Div(id='dummy-output', style={'display': 'none'})

])


index_page = html.Div(children = 
                      [

    html.Div([
    html.Img(src='/assets/mediolanum.png', id='logo'),  # Add this line to your layout
    html.Img(src='/assets/apex_white.png', id='apex'),

    dcc.Store(id='init', data=0),
    html.Div(id='dummy-output', style={'display': 'none'}) , 
        dcc.Link([
            html.Div([
                html.Div(style={'--url': "url('https://i.ibb.co/PM4ghD4/full.png')"}, className='shadow'),
                html.Div(style={'--url': "url('https://i.ibb.co/JpJVJxq/Background.png')"}, className='image background'),
                html.Div(style={'--url': "url('https://i.ibb.co/Dw3q3tZ/cutout.png')"}, className='image cutout'),
                html.Div([
                    html.H2('Create your own Backtest'),
                    html.P('Perform a backtest using the QPS backtest engine with your own custom parameters.')
                ], className='content')
            ], className='card border-left-behind'),
        ], href='https://github.com/', target='_blank'),
        dcc.Link([
            html.Div([
                html.Div(style={'--url': "url('https://i.ibb.co/DC0MbxS/m-full.png')"}, className='shadow'),
                html.Div(style={'--url': "url('https://i.ibb.co/ZdGBm4K/m-background.png')"}, className='image background'),
                html.Div(style={'--url': "url('https://i.ibb.co/RC70XmC/m-cutout.png')"}, className='image cutout'),
                html.Div([
                    html.H2('Load a pre-existing Backtest'),
                    html.P('Connect to QPS databases and load a previously saved backtest.')
                ], className='content')
            ], className='card border-right-behind border-bottom-behind'),
        ], href='https://example.com', target='_blank'),
        dcc.Link([
            html.Div([
                html.Div(style={'--url': "url('https://i.ibb.co/gSBp82C/b-full.png')"}, className='shadow'),
                html.Div(style={'--url': "url('https://i.ibb.co/MDBcyMW/b-background.png')"}, className='image background'),
                html.Div(style={'--url': "url('https://i.ibb.co/bQNgD6y/b-cutout.png')"}, className='image cutout'),
                html.Div([
                    html.H2('Live Portfolio Tools!'),
                    html.P('Launch the QPS live portfolio tools to monitor the QPS portfolios in real time.')
                ], className='content')
            ], className='card border-left-behind')
        ], href='/live_dash')
    ], className='centered'),
    html.Canvas(id='canvas1'),
    dcc.Location(id='url', refresh=False),
    #html.Script(src='/assets/script.js')
], className = 'Body')

app.clientside_callback(
    """
    function(pathname) {
        if (pathname) { // Checks if pathname is not null or undefined
            setTimeout(function(){
                runCanvas();
            }, 1);
        }
        return '';
    }
    """,
    Output('dummy-output', 'children'),
    [Input('url', 'pathname')]
)


@app.callback(
    Output('current-pathname', 'data'),
    Input('url', 'pathname'),
    State('current-pathname', 'data')
)
def update_current_pathname(new_pathname, current_pathname):
    if new_pathname != current_pathname:
        return new_pathname
    return dash.no_update

@app.callback(
    Output('page-content', 'children'),
    Input('current-pathname', 'data')
)
def display_page(pathname):
    if pathname == '/live_dash':
        return web_trial.app.layout
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(debug=True)

