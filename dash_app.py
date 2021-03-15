import dash 
import sqlite3
import dash_core_components as dcc 
import dash_html_components as html 
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

external_stylesheets = ["https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap-grid.min.css"]
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

# these colors aren't defined in CSS because graphs don't accept CSS styling
colors = {"background" : "#05101E", "text_base" : "#E0E0E0"}
chart_layout = {
    "font" : dict(
        family = "poppins",
        size = 20,
        color = colors["text_base"]),
    "paper_bgcolor" : "rgba(0,0,0,0)",
    "plot_bgcolor" : "rgba(0,0,0,0)",
    "height" : 700
}

def build_title():
    return html.Div(id = "title-banner", children = [
        html.H1("Twitch Data Visualization Dashboard", id="app-title"),
        html.Img(
            id = "twitch-icon", 
            alt = "twitch icon", 
            src = app.get_asset_url("twitch_icon.png"),
            height = 20
        ),  
        html.A("Built Live by Mitch Harrison", id = "app-subtitle", href = "https://twitch.tv/MitchsWorkshop")
    ])


def get_chat_messages():
    conn = sqlite3.connect("data.db")
    with conn:
        df = pd.read_sql("SELECT * FROM chat_messages", conn)
    return df


def build_chatter_slider():
    df = get_chat_messages()
    num_chatters = len(df["user"].unique())
    slider_max = 50 if num_chatters > 50 else num_chatters
    step = slider_max // 15
    return dcc.Slider(
                id = "top-chatter-number",
                min = 1,
                max = slider_max,
                value = slider_max // 2,
                marks = {i : str(i) for i in range(1,slider_max, step)},
                # step = step
            )


def build_footer():
    return html.Div(id = "discord-footer", children = [
        html.Span(id = "discord-icon", children = [
            html.Img(
                alt = "discord icon",
                src = app.get_asset_url("discord_icon.png") ,
                height = 22
            )
        ]),
        html.A(
            "Join the Discord for discussion!", 
            id = "discord-cta", 
            href = "https://discord.gg/7nefPK6"
        )
    ])


# top chatters bar graph
@app.callback(
    Output(component_id="bar-top-chatters", component_property="figure"),
    [Input(component_id="top-chatter-number", component_property="value"),
    Input(component_id="interval-counter", component_property="n_intervals")]
)
def bar_top_chatters(top_num: int, n:int) -> go.Figure:
    df = get_chat_messages()
    data = df["user"].value_counts().reset_index()
    data.columns = ["user", "message_count"]
    trace_data = data.head(top_num)

    trace = go.Bar(
        x = trace_data["user"],
        y = trace_data["message_count"]
    )

    fig = go.Figure(data = [trace], layout = chart_layout)
    fig.update_layout({
        "title" : dict(
            text = f"Top {top_num} Chatters - All Time",
            font = dict(
                family = "poppins", 
                size = 35, 
                color = colors["text_base"]
                )
            )
        })
    return fig


# command use bar graph
@app.callback(
    Output(component_id = "bar-top-commands", component_property = "figure"),
    [Input(component_id = "interval-counter", component_property = "n_intervals")]
)
def bar_command_use(n: int) -> go.Figure:
    conn = sqlite3.connect("data.db")
    with conn:
        df = pd.read_sql("SELECT * FROM command_use", conn)
    
    data_custom = df[df["is_custom"]==True]
    data_custom = data_custom["command"].value_counts().reset_index()
    data_custom.columns = ["command", "count"]

    data_hard_coded = df[df["is_custom"]==False]
    data_hard_coded = data_hard_coded["command"].value_counts().reset_index()
    data_hard_coded.columns = ["command", "count"]

    trace1 = go.Bar(
        x = data_custom["command"],
        y = data_custom["count"],
        name = "Custom"
    )
    trace2 = go.Bar(
        x = data_hard_coded["command"],
        y = data_hard_coded["count"],
        name = "Default"
    )

    fig = go.Figure(data = [trace1, trace2], layout = chart_layout)
    fig.update_layout({
        "title" : dict(
            text = f"Top Commands Used - All Time",
            font = dict(
                family = "poppins", 
                size = 35, 
                color = colors["text_base"]
                ),
            ),

        'xaxis': dict(
            categoryorder = 'array',
            categoryarray = list(df["command"].value_counts().index)
        ),

        "legend" : dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            itemclick=False)
        })
    return fig


# start of app 
app.layout = html.Div([
    dbc.Row(dbc.Col(build_title())),

    dbc.Row(
        dbc.Col(
            build_chatter_slider(),
            width = {"size":9, "offset":3}
        )
    ),

    dbc.Row([
        dbc.Col(dcc.Graph(id = "bar-top-commands"), width = 3),
        dbc.Col(dcc.Graph(id = "bar-top-chatters"))
    ]),

    dcc.Interval(
        id = "interval-counter",
        interval = 3 * 1000, # in milliseconds
        n_intervals = 0
    ),

    dbc.Row(dbc.Col(build_footer()))
])


if __name__ == '__main__':
    app.run_server(debug=True)
