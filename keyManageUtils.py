import pandas as pd
import numpy as np
import networkx as nx
import random
import gravis as gv


def read_file(filepath):

    df = pd.read_excel(filepath)
    new_header = df.iloc[0]
    df.columns = new_header
    df = df[3:]

    # check door name if not use "NoDoor/ドアなし"
    columns_to_check = ['建具 種類'] 
    for col in columns_to_check:
        if col not in df.columns:
            df[col] = 'ドアなし'
        else:
            df[col] = df[[col]].apply(lambda x: x.fillna('ドアなし') if x.isna().any() else x)

    # check all numerical columns if not fill with 0
    columns_to_check = ['建具 番号', '部屋から: 番号','部屋へ: 番号']
    for col in columns_to_check:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = df[[col]].apply(lambda x: x.fillna(0) if x.isna().any() else x)

    # Drop NaN values in '部屋から: 名前' and '部屋へ: 名前', '部屋から: レベル', '部屋へ: レベル'
    columns_to_check = ['部屋から: 名前', '部屋へ: 名前', '部屋から: レベル', '部屋へ: レベル']
    df = df.dropna(subset=columns_to_check)

    # if no セキュリティレベル then replace with レベルなし
    columns_to_check = ['部屋から: セキュリティレベル', '部屋へ: セキュリティレベル'] # ['部屋から: コメント', '部屋へ: コメント']
    for col in columns_to_check:
        if col not in df.columns:
            df[col] = 'レベルなし'
        else:
            df[col] = df[[col]].apply(lambda x: x.fillna('レベルなし') if x.isna().any() else x)

    # Convert numeric columns to integer
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].astype(int)
    
    return df



def calculate_first_node_position(G):
    # set location for the nodes
    G1 = nx.Graph(list(G.edges))
    check_nodes = G1.nodes()
    if '外部' in check_nodes:
        check_nodes = ['外部']
    
    max_path_length = 0
    for start in check_nodes:
        for end in G1.nodes():
            if start != end:
                all_paths = nx.all_simple_paths(G1, source=start, target=end) # find_all_paths1(graph1, start, end, path=[])
    
                for path in all_paths:
                    # print(f"{len(path)}: {path}")
                    if len(path) > max_path_length:
                        max_path = path
                        max_path_length = len(path)

    previous_nodes = max_path.copy()
    connection_node_list = []
    total_used_node_len = 0
    for ndix in range(len(max_path)):

        curr_node = max_path[ndix]
        new_nodes = list(G.predecessors(curr_node)) + list(G.successors(curr_node))

        set1 = set(previous_nodes)
        set2 = set(new_nodes)
        connected_nodes = list(set2 - set1)
        
        same_line_nodes = [[i] for i in connected_nodes]
        same_line_nodes1 = [[i] for i in connected_nodes]
        num = len(connected_nodes)

        while num > 0:
            temp_list = []
            temp_num = 0
            for k, lst_node in enumerate(same_line_nodes1):
                if len(lst_node) > 0:
                    for conn_node in lst_node:
                        new_nodes1 = list(G.predecessors(conn_node)) + list(G.successors(conn_node))

                        set1 = set(previous_nodes)
                        set2 = set(new_nodes1)
                        connected_nodes1 = list(set2 - set1)
                        same_line_nodes[k] += connected_nodes1

                        temp_num += len(connected_nodes1)
                        previous_nodes += connected_nodes1
                        previous_nodes.append(conn_node)
                else:
                    connected_nodes1 = []

                temp_list.append(connected_nodes1)
                
            same_line_nodes1 = temp_list
            num = temp_num
                
        connection_node_list.append(same_line_nodes)

    # print(connection_node_list)
    # print(previous_nodes)
    total_used_node_len = len(previous_nodes)
    total_used_nodes = previous_nodes.copy()
    total_nodes = list(G.nodes)

    x_cord, y_cord = 0,0
    pos = {}
    pos_list = []
    for node_i, node_l in enumerate(max_path):
        if node_i % 4 in [0, 1]:
            factor = 0.0
        else:
            factor = 1.0

        if node_i % 2 == 0:
            x, y = x_cord+1+factor, y_cord
        else:
            x, y = x_cord-1-factor, y_cord
        
        if len(connection_node_list[node_i]) == 0:
            y_cord += 1
        else:
            y_cord += 2
        pos[node_l] = (x, y)
        pos_list.append([x,y])
    

    for node_j, node_k in enumerate(connection_node_list):
        len_node_list = len(node_k)
    
        if len_node_list > 0:
            # print(node_k)
            cal_len_node_list = sum([len(i) for i in node_k])
            if cal_len_node_list == len_node_list:
            
                x1, y1 = 2, pos_list[node_j][1]
                x2, y2 = -2, pos_list[node_j][1]
                num = 0
                factor1= factor2 = 0.0
                for node_m, node_n in enumerate(node_k):
                    if node_m < len_node_list//2:
                        for _, node_q in enumerate(node_n):
                            x1 += 2
                            if num % 2 == 0:
                                pos[node_q] = (x1, y1-0.7+factor1)
                            else:
                                pos[node_q] = (x1, y1+0.7-factor1)
                            
                            num+=1
                            factor1 += 0.05
                    else:
                        for _, node_q in enumerate(node_n):
                            x2 -= 2
                            if num % 2 == 0:
                                pos[node_q] = (x2, y2+0.7-factor2)
                            else:
                                pos[node_q] = (x2, y2-0.7+factor2)
                    
                            num+= 1
                            factor2+=0.05
            else:

                x1, y1 = 2, pos_list[node_j][1]
                x2, y2 = -2, pos_list[node_j][1]
                num1 = num2 = 0
                factor1 = factor2 = 0.0
                for node_m, node_n in enumerate(node_k):
                    if len(node_n) != 1:
                        # x1, y1 = 2, pos_list[node_j][1]
                        for _, node_q in enumerate(node_n):
                            x1 += 2.5
                            if num1 % 2 == 0:
                                pos[node_q] = (x1, y1-0.8+factor1)
                            else:
                                pos[node_q] = (x1, y1+0.8-factor1)
                    
                            num1+= 1
                            factor1+=0.1
                        #     x1 += 2.5
                        #     if num1 % 2 == 0:
                        #         pos[node_q] = (x1, y1+0.5-factor1+0.25)
                        #     else:
                        #         pos[node_q] = (x1, y1+0.5-factor1-0.25)
                            
                        #     num1+=1
                        # factor1+=0.5
                    else:
                        for _, node_q in enumerate(node_n):
                            x2 -= 2.0
                            if num2 % 2 == 0:
                                pos[node_q] = (x2, y2-0.8+factor2)
                            else:
                                pos[node_q] = (x2, y2+0.8-factor2)
                    
                            num2+= 1
                            factor2+=0.05


    if len(total_nodes) != total_used_node_len:
        set1 = set(total_nodes)
        set2 = set(total_used_nodes)
        unused_nodes = list(set1 - set2)

        # Get the connected components
        connected_components = list(nx.connected_components(G1))
        # Print the connected components
        x_cord = -6
        y_cord += 1
        factor1 = 0.1
        for i, component in enumerate(connected_components, 1):
            unused_nodes_list= list(component)
            if unused_nodes_list[0] in unused_nodes:
            
                # print(f"Connected Component {i}: {component}")
                for i in range(len(unused_nodes_list)):
                    if i % 2 == 0:
                        pos[unused_nodes_list[i]] = (x_cord, y_cord-1.0+factor1)
                    else:
                        pos[unused_nodes_list[i]] = (x_cord, y_cord+1.0-factor1)
                    x_cord+=2
                    factor1+=0.1
    
    return pos


def draw_graph_floorwise(dataframe, name_graph=None, graph_type=None):

    node_to_color_yellow = ['外部', 'エントランスホール', '廊下(1)', '廊下(2)', '廊下(3)', 'EVホール (EV1)', 'EVホール(EV1)', 'クリーン廊下', '廊下']

    new_df = dataframe.loc[dataframe['部屋から: レベル'] == name_graph]

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges with labels
    for _, row in new_df.iterrows():

        if graph_type == 'vis':
            from_node = f'''{row['部屋から: レベル']} \n {row['部屋から: 名前']}({row['部屋から: 番号']}) \n {row['部屋から: セキュリティレベル']}'''
            to_node = f'''{row['部屋へ: レベル']} \n {row['部屋へ: 名前']}({row['部屋へ: 番号']}) \n {row['部屋へ: セキュリティレベル']}'''
        else:
            from_node = f'''{row['部屋から: 名前']}({row['部屋から: 番号']})'''
            to_node = f'''{row['部屋へ: 名前']}({row['部屋へ: 番号']})'''
        
        
        
        edge_label = f"{row['建具 種類']}/{row['建具 番号']}"#({row['部屋へ: レベル']})"
        floor_from = '#87CEFA'
        floor_to = '#87CEFA'

        if row['部屋から: 名前'] in node_to_color_yellow:
            floor_from = 'yellow'     #row['部屋から: セキュリティレベル']  # Floor level of 'from' node
        if row['部屋へ: 名前'] in node_to_color_yellow:
            floor_to = 'yellow'  # row['部屋へ: セキュリティレベル']  # Floor level of 'to' node

        edge_color = '#BDB7AB'

        G.add_node(row['部屋から: 名前'], color=floor_from, label=from_node)  # Add floor level as node attribute
        G.add_node(row['部屋へ: 名前'], color=floor_to, label=to_node)      # Add floor level as node attribute edge_colors_list_choice
        G.add_edge(row['部屋から: 名前'], row['部屋へ: 名前'], label=edge_label, color = edge_color, weight=4, arrows=True)

    
    node_pos = calculate_first_node_position(G)
    G_undirected = G.to_undirected()
    node_info = gv.convert.networkx_to_gjgf(G_undirected)


    # Merge node_info and node_pos to include position information
    for node, pos in node_pos.items():
        if node in node_info['graph']['nodes']:
            node_info['graph']['nodes'][node]['metadata']['x'] = pos[0]*75
            node_info['graph']['nodes'][node]['metadata']['y'] = -pos[1]*100

            node_info['graph']['nodes'][node]['metadata']['border_color'] = 'black'
            node_info['graph']['nodes'][node]['metadata']['border_size'] = 2

    # print(node_info)
    if graph_type == 'd3':
        fig = gv.d3(node_info, graph_height=620, show_node_label_border=True,show_menu=True,
                node_size_factor=5, node_label_size_factor=2, show_node_label=True, node_label_data_source='label',
                edge_label_size_factor=2, show_edge_label=True, edge_label_data_source='label', edge_size_data_source='weight', 
                layout_algorithm_active=False, node_drag_fix=True)
    elif graph_type == 'three':
        fig = gv.three(node_info, graph_height=620, show_node_label_border=True,show_menu=True,
                node_size_factor=5, node_label_size_factor=2, show_node_label=True, node_label_data_source='label',
                edge_label_size_factor=2, show_edge_label=True, edge_label_data_source='label', edge_size_data_source='weight', 
                layout_algorithm_active=False, node_drag_fix=True)
    else:
        fig = gv.vis(node_info, graph_height=620, show_node_label_border=True,show_menu=True,
                node_size_factor=5, node_label_size_factor=2, show_node_label=True, node_label_data_source='label',
                edge_label_size_factor=2, show_edge_label=True, edge_label_data_source='label', edge_size_data_source='weight', 
                layout_algorithm_active=False, node_drag_fix=True)
    
    html_text = fig.to_html()
    # Encode the HTML text with UTF-8
    html_text_utf8 = html_text.encode('utf-8')
    # # Write the encoded HTML text to a file
    # with open('./static/graph.html', 'wb') as file_handle:
    #     file_handle.write(html_text_utf8)

    # Get the list of nodes
    node_list = list(G.nodes())
    # Get the list of from nodes
    from_nodes = list(set([edge[0] for edge in G.edges()])) 
    # Get the list of to nodes
    to_nodes = list(set([edge[1] for edge in G.edges()])) 
    
    return html_text_utf8, node_list, from_nodes, to_nodes, node_info


def modify_colors(node_info, node_color_comb=None, edge_color_comb=None, graph_type=None):
    # Node color map
    # node_lists = [['機械室', '#ee4f4f'], ['更衣室', '#524242'], ['廊下1', '#e50b0b'], ['書庫', '#b44141'], ['書庫', '#370b0b']]
    if node_color_comb:
        node_color_map = dict(node_color_comb)

        # Update node colors
        for node_name, node_data in node_info['graph']['nodes'].items():
            if node_name in node_color_map:
                node_data['metadata']['color'] = node_color_map[node_name]

    # edge_color_comb = [['廊下1', '階段室１', '#e02e2e'], ['外部', '廊下1', '#9c4040'], ['社長室', '更衣室', '#805b5b']]
    # Edge connection color map
    if edge_color_comb:
        edge_color_map = {(edge[0], edge[1]): edge[2] for edge in edge_color_comb}

        # Update edge connection colors
        for edge_data in node_info['graph']['edges']:
            edge_from = edge_data['source']
            edge_to = edge_data['target']
            edge_connection1 = (edge_from, edge_to)
            if edge_connection1 in edge_color_map:
                edge_data['metadata']['color'] = edge_color_map[edge_connection1]
            edge_connection2 = (edge_to, edge_from)
            if edge_connection2 in edge_color_map:
                edge_data['metadata']['color'] = edge_color_map[edge_connection2] 

    # Print modified node_info
    # print(node_info)
    if graph_type == 'd3':
        fig = gv.d3(node_info, graph_height=620, show_node_label_border=True,show_menu=True,
                node_size_factor=5, node_label_size_factor=2, show_node_label=True, node_label_data_source='label',
                edge_label_size_factor=2, show_edge_label=True, edge_label_data_source='label', edge_size_data_source='weight', 
                layout_algorithm_active=False, node_drag_fix=True)
    elif graph_type == 'three':
        fig = gv.three(node_info, graph_height=620, show_node_label_border=True,show_menu=True,
                node_size_factor=5, node_label_size_factor=2, show_node_label=True, node_label_data_source='label',
                edge_label_size_factor=2, show_edge_label=True, edge_label_data_source='label', edge_size_data_source='weight', 
                layout_algorithm_active=False, node_drag_fix=True)
    else:
        fig = gv.vis(node_info, graph_height=620, show_node_label_border=True,show_menu=True,
                node_size_factor=5, node_label_size_factor=2, show_node_label=True, node_label_data_source='label',
                edge_label_size_factor=2, show_edge_label=True, edge_label_data_source='label', edge_size_data_source='weight', 
                layout_algorithm_active=False, node_drag_fix=True)
    

    html_text = fig.to_html()
    # Encode the HTML text with UTF-8
    html_text_utf8 = html_text.encode('utf-8')

    return node_info, html_text_utf8


