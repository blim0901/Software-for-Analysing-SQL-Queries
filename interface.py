"""
contains code for GUI
"""

import annotation
from preprocessing import *
import PySimpleGUI as sg
import tkinter as tk
import Pmw
import subprocess
import sqlparse

class GUI1():

    def __init__(self):
        return

    def initialise_GUI1(self):

        sg.theme('DefaultNoMoreNagging') #theme of GUI
        font = 'Arial'#'Consolas'

        # All the stuff inside the window.

        # Frame 0: Control Settings
        frame0_layout = [[ sg.Button('Exit')]]

        col1 = [
            [sg.Text('Host:', font=(font, 12), justification='left')],
            [sg.Text('Port:', font=(font, 12), justification='left')],
            [sg.Text('Database:', font=(font, 12), justification='left')],
            [sg.Text('Username:', font=(font, 12), justification='left')],
            [sg.Text('Password:', font=(font, 12), justification='left')],
            [sg.Text('Enter Query:', font=(font, 12), justification='left')],
        ]
    
        col2 = [
            [sg.Input(key='host', font=(font, 12), default_text='localhost')],
            [sg.Input(key='port', font=(font, 12), default_text='5432')],
            [sg.Input(key='database', font=(font, 12), default_text='TPC-H')],
            [sg.Input(key='username', font=(font, 12), default_text='postgres')],
            [sg.InputText('', key='password', password_char='*', font=(font, 12))],
            [sg.Multiline(
                size=(45, 15),
                key="query", 
                font=(font, 12), 
                autoscroll=True,
            )],
            [sg.Stretch(), sg.Text("", key='-MSG-', text_color='darkblue')],
            [sg.Stretch(), sg.Button('Submit')]
        ]

        # Frame 1: Login and Provide Query
        frame1_layout = [
            [sg.Frame(layout=col1, title='', pad = 5, expand_x = True, vertical_alignment="top", border_width=0, element_justification = 'center'), sg.Frame(layout=col2, title='', pad = 5, expand_x = True, element_justification = 'center')]
        ]

        layout = [
            [sg.T('CZ4031 Query Execution Plan Annotator', font='_ 16', justification='l', background_color='darkblue', text_color='papaya whip', expand_x=True)],
            [sg.Frame('Control Settings', frame0_layout, pad = 5, expand_x = True, element_justification = 'right')],
            [sg.Frame('Step 1: Login and Provide Query', frame1_layout, pad = 5, expand_x = True, element_justification = 'center')],
            # [sg.Button('Submit', button_color=('white', 'green'))]
        ]

        # Nesting the above into a column so as to allow vertical scrolling
        layout2 = [
            [sg.Column(layout, scrollable = True, expand_y = True, expand_x = True, size=(1500,3000),element_justification='center')]
        ]

        # Create the Window
        window = sg.Window('CZ4031 Database Project 2 GUI', layout2, size=(700, 990), resizable=True, element_justification='c').Finalize()
        # window.Maximize()
        
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Exit': # if user closes window or clicks cancel
                break

            if event == 'Submit':   # when user clicks submit button
                inputs = ['host', 'port', 'database', 'username', 'password', 'query']

                # get all inputs
                host = values['host'].lower()   #localhost
                port = values['port']   #5432
                database = values['database']   #whatever ur database name is
                username = values['username'].lower()   #postgres
                password = values['password']   #whatever ur password is
                query = values['query'] #get query

                single_line_query = ''
                for text in query.split('\n'):
                    single_line_query += text.strip() + ' '

                # # error checking for all the above inputs
                # for input in inputs:
                #     if getattr(other, input) == '':
                #         values['-MSG-'].update("Please enter a" + input + "!")

                # window['-MSG-'].update("Query Submitted to PostgreSQL! Please wait for results! ")
                sg.SystemTray.notify('Query Submitted to PostgreSQL!', 'Please wait for results!', display_duration_in_ms = 1000, fade_in_duration = 0)
                return host, port, database, username, password, single_line_query, window
            
        window.close()

class GUI2():

    def __init__(self):
        return

    def initialise_GUI2(self, query, query_plan, query_plan_costs, query_plan_scenarios):

        sg.theme('DefaultNoMoreNagging') #theme of GUI
        font = 'Arial'

        # All the stuff inside the window.

        # Frame 0: Control Settings
        col1 = [
            [sg.Button('Back')]
        ]
        col2 = [
            [sg.Button('Exit')]
        ]
        frame0_layout = [
            [sg.Frame(layout=col1, title='', vertical_alignment="top", border_width=0, element_justification = 'center'), sg.Frame(layout=col2, title='', border_width=0, element_justification = 'center')]
        ]

        # Frame 2: Display QEP and Output
        
        # list of nodes of the optimal query plan
        optimal_qep_nodes = []
        for element in query_plan:
            if element != '':
                optimal_qep_nodes.append(element)
        
        # list of query_frags of the optimal query plan
        query_frag_list = []
        for element in optimal_qep_nodes:
            query_frag_list.append(element.query_frag)
        
        # color to match query with annotation
        color_list = ['dark orange', 'orchid1', 'turquoise3', 'medium sea green', 'gold4', 'chartreuse3', 'rosy brown', 'deep sky blue', 'DarkOliveGreen4', 'coral1', 'DarkCyan', 'salmon1', 'wheat4', 'DarkMagenta','DarkOrange3', 'cornflower blue', 'GreenYellow', 'plum3', 'sienna3', 'medium violet red', 'MistyRose3', 'OrangeRed3']
        colors = {}
        for i in range(0,len(optimal_qep_nodes)):
            colors[optimal_qep_nodes[i]] = color_list[i]

        # make input query text look nice
        pretty_query_text = sqlparse.format(query, reindent=True, keyword_case='upper')

        # split query by operators to match query_frag
        pretty_query_text_2 = []
        temp_text = ''
        for text in query.split(' '):
            if text == 'FROM':
                pretty_query_text_2.append(temp_text.strip())
                temp_text = 'FROM '
            elif text == 'WHERE':
                pretty_query_text_2.append(temp_text.strip())
                temp_text = 'WHERE '
            elif text == 'GROUP':
                pretty_query_text_2.append(temp_text.strip())
                temp_text = 'GROUP '
            elif text == 'ORDER':
                pretty_query_text_2.append(temp_text.strip())
                temp_text = 'ORDER '
            elif text == 'LIMIT':
                pretty_query_text_2.append(temp_text.strip())
                temp_text = 'LIMIT '
            else:
                temp_text += text + " "
        pretty_query_text_2.append((temp_text.strip()))

        # Frame 2 layouts

        # Canvas to draw tree
        canvas_layout = [
            [sg.Canvas(size=(1000,1500), background_color='white', key= 'canvas',)],  
        ]
        canvas_column_layout = [
            [sg.Column(canvas_layout, scrollable = True, element_justification='center', size=(1000,300))]  
        ]

        # Query Annotations
        annotation_layout = [
            [sg.Text('Query Plan Annotation and Statistics', font=(font, 12), justification='left',background_color='darkblue', text_color='papaya whip', expand_x=True)],
        ]
        annotation_layout += [[sg.Text(f'{i.annotation_text} ',size=(60,None), text_color=colors[i])] for i in optimal_qep_nodes]

        # Input query text
        query_text_layout = [
            [sg.Text('Input Query', font=(font, 12), justification='left',background_color='darkblue', text_color='papaya whip', expand_x=True)],
        ]

        # display input query with color corresponding to annotations
        for i in pretty_query_text_2:
            match = 0
            for j in optimal_qep_nodes:
                if (j.query_frag).strip().lower() == i.strip().lower():
                    query_text_layout += [[sg.Text(i, size=(60,None), text_color = colors[j])]]
                    match = 1
                    break
            if match == 0:
                query_text_layout += [[sg.Text(i, size=(60,None),text_color = 'darkblue')]]

        # frame 2 layout
        frame2_layout = [
            [sg.Text('Query Plan Operator Tree', font=(font, 12), justification='left',background_color='darkblue', text_color='papaya whip', expand_x=True)],
            [sg.Frame(layout=canvas_column_layout, title='', pad = 5, expand_x = True, vertical_alignment="top", border_width=0, element_justification = 'left')],
            [sg.Text(' ', font=(font, 12))], # just empty space to space it out
            [
                sg.Frame(layout=query_text_layout, title='', pad = 5, expand_x = True, vertical_alignment="top", border_width=0, element_justification = 'left'), 
                sg.Frame(layout=annotation_layout, title='', pad = 5, expand_x = True, vertical_alignment="top", border_width=0, element_justification = 'left')
            ],
        ] 

        # Frame 3: Display Cost of Alternative Query Plans

        # list of AQPs
        aqp_details = []
        for i in range(1,len(query_plan_scenarios)):
            aqp_details.append(query_plan_scenarios[i][:-8] + ': ' + str(query_plan_costs[i]))
        optimal_cost = query_plan_scenarios[0] + ": " + str(query_plan_costs[0])
        
        # AQP 
        aqp_layout = [
            [sg.Text(f'{aqp} ')] for aqp in aqp_details
        ]

        # frame 3 layout
        frame3_layout = [ 
            [sg.Text('Cost of current optimal Query Plan', font=(font, 12), justification='left',background_color='darkblue', text_color='papaya whip', expand_x=True)],
            [sg.Text(optimal_cost)],
            [sg.Text('Cost of alternative Query Plans', font=(font, 12), justification='left',background_color='darkblue', text_color='papaya whip', expand_x=True)],
            [sg.Frame(layout = aqp_layout, title='', pad = 5, expand_x = True, vertical_alignment="top", border_width=0, element_justification = 'left')]
        ]

        # window layout
        layout = [
            [sg.Text('CZ4031 Query Execution Plan Annotator', font='_ 16', justification='l', background_color='darkblue', text_color='papaya whip', expand_x=True)],
            [sg.Frame('Control Settings', frame0_layout, pad = 5, expand_x = True, element_justification = 'right')],
            [sg.Frame('Step 2: Display QEP and Output', frame2_layout, pad = 5, expand_x = True, element_justification = 'l')],
            [sg.Frame('Step 3: Display Cost', frame3_layout, pad = 5, expand_x = True, element_justification = 'l')],
        ]

        # Nesting the above into a column so as to allow vertical scrolling
        layout2 = [
            [sg.Column(layout, scrollable = True, expand_y = True, expand_x = True, size=(1100,2400),element_justification='center')]
        ]

        # Create the Window
        window = sg.Window('CZ4031 Database Project 2 GUI', layout2, resizable=True, element_justification='c').Finalize()
        #window.Maximize()

        # Draw tree on canvas
        canvas = window['canvas']
        for element in optimal_qep_nodes:
            element.x1 = element.x1  # + offset
            element.x2 = element.x2  # + offset

        # store unique coordinates
        unique_coordinates = []
        for element in optimal_qep_nodes:
            # element.x1 = element.x1 + offset
            # element.x2 = element.x2 + offset

            coordinates = (element.x1, element.x2, element.y1, element.y2)
            if coordinates not in unique_coordinates:
                unique_coordinates.append(coordinates)
            else:
                element.x1 += 3*annotation.BOX_W/2
                element.x2 += 3*annotation.BOX_W/2
                element.center = ((element.x1+element.x2)/2,(element.y1+element.y2)/2)
                new_coor = (element.x1, element.x2, element.y1, element.y2)
                unique_coordinates.append(new_coor)
        
        # create rectangles
        for element in optimal_qep_nodes:
            x1 = element.x1 #+ offset
            x2 = element.x2 #+ offset
            y1 = element.y1
            y2 = element.y2
            rect = canvas.TKCanvas.create_rectangle(x1, y1, x2, y2, fill=colors[element])
            canvas.TKCanvas.itemconfig(rect)

            # create tooltip
            balloon = Pmw.Balloon()
            balloon.tagbind(canvas.TKCanvas, rect, element.annotation_text)
            annotation.visual_to_node[rect] = element

        # create text on rectangles
        for element in optimal_qep_nodes:
            gui_text = canvas.TKCanvas.create_text((element.center[0], element.center[1]), text=element.op_type)
            canvas.TKCanvas.itemconfig(gui_text)
            annotation.visual_to_node[gui_text] = element

        # create arrows
        for element in optimal_qep_nodes:
            for child in element.pointers:
                line = canvas.TKCanvas.create_line(child.center[0], child.center[1] - annotation.BOX_H/2, element.center[0],
                                element.center[1] + annotation.BOX_H/2, arrow = tk.LAST)
                canvas.TKCanvas.itemconfig(line)
        
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()      
            
            if event == sg.WIN_CLOSED or event == 'Exit': # if user closes window or clicks cancel
                break
            if event == 'Back':
                window.close()
                subprocess.run('python project.py')

        window.close()

def main():
    app = GUI1()
    app.initialise_GUI1()

if __name__ == "__main__":
    main()