from preprocessing import *
import interface
import annotation


if __name__ == '__main__':

    host, port, database, username, password, query, window = interface.GUI1().initialise_GUI1()
    connect = Preprocessing(host, port, database, username, password)

    parsed_query = connect.process_query(query=query)

    # # Can use this generated_plans to get access to the json for each of the different. It is an array of json string. Each index represents one query plan
    generated_plans = connect.generate_plans(query)

    # Print the total number of alternative plans
    print('There are a total of ' + str(len(generated_plans)) + ' plans generated')

    # Print the QEP. The QEP is at the index 0 of generated_plans
    print('This is how the chosen QEP looks like:')
    print(generated_plans[0])

    #global costs_of_all_plans 
    costs_of_all_plans = calculate_costs(generated_plans)

    # Here is an array storing the costs of each of the plans in generated_plans. The position of each cost in the array
    # is the same as the position of the query plan in generated_plans, so can map the costs accordingly.
    # The cost at index position 0 is the most optimized one, for the chosen query plan
    # need to pass back to annotation.py to annotate the nodes with the relative costs
    print("Costs of each of the plans: ")
    print(costs_of_all_plans)

    # Here is an array storing the condition that is disabled (scenario) for each of the plans. The first one is just
    # the optimized query
    scenario_of_all_plans = get_scenarios()
    print("Scenarios of each of the plans: ")
    print(scenario_of_all_plans)

    # For the GUI edit the starting values of x1, y1, x2, y2 here
    annotation.overall_nodes.clear()
    root_node = Node(425, 10, 425 + annotation.BOX_W, 10 + annotation.BOX_H, "", "", "", 0)
    # This the QEP that has been converted into a tree structure.
    qep = build_tree(root_node, generated_plans[0])
    qep_with_comparison = add_comparison_values(qep)

    # matching annotation to query
    connect.match_nodes_to_query(query, qep_with_comparison)
    
    # -------------------------------------
    results = connect.parse_query(query)

    window.close()
    interface.GUI2().initialise_GUI2(query, qep_with_comparison, costs_of_all_plans, scenario_of_all_plans)

