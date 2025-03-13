import traci
from configs.set_parameters import set_parameters
from environment.single_intersection import SingleIntersection
from agent.mpc_agent import MpcAgent

def scenario(network_type, volume_type, control_type, parameter_name, parameter_value):
    print("----Get parameters...")
    paras = set_parameters(network_type, volume_type)

    paras[parameter_name] = parameter_value

    print("----Build single intersection environments...")
    env_single_intersection = SingleIntersection(paras)

    print("----Start SUMO...")
    env_single_intersection.start_sumo(True, control_type, network_type, volume_type)

    print("----Initializing the agent...")
    agent_unified_four_legs_three_lanes = MpcAgent(paras, "unified_four_legs_three_lanes")
    agent_unified_four_legs_three_lanes.clear_redundant_gams_files()

    phase_list_multi=[]
    duration_list_multi=[]
    step = 0
    while env_single_intersection.is_active():

        print(f"----Get network state at step {step}")
        network_state = env_single_intersection.get_state_cur_intersection(step)

        if control_type == "multi_scale":
            # print("----Get control commands from the agent")
            (next_global_step_to_re_solve_the_network, phase_list_multi, duration_list_multi, should_update_signal, next_signal_phase, speed_commands) = (
                agent_unified_four_legs_three_lanes.get_control_commands(
                    paras, network_state, step
                )
            )
            env_single_intersection.apply_control_commands(
                should_update_signal, next_signal_phase, speed_commands
            )

        elif control_type == "actuated":
             env_single_intersection.pedestrian_actuation()

            #env_single_intersection.pedestrian_movement_control()
        env_single_intersection.calculate_extra_metrics()
        env_single_intersection.move_one_step_forward()
        step += 1
        print(f"-------------------------------")

    env_single_intersection.close_sumo_simulation()
    name = str(parameter_name) + '_' + str(parameter_value)
    env_single_intersection.performance_results_scenario(phase_list_multi, duration_list_multi, network_type, volume_type, control_type, step, name)
    agent_unified_four_legs_three_lanes.clear_redundant_gams_files()

def scenario_base(network_type, volume_type, control_type, ped_phasing_val, pene_value):
    print("----Get parameters...")
    paras = set_parameters(network_type, volume_type)

    paras["ped_phasing"] = ped_phasing_val
    paras["penetration"] = pene_value

    print("----Build single intersection environments...")
    env_single_intersection = SingleIntersection(paras)

    print("----Start SUMO...")
    env_single_intersection.start_sumo(True, control_type, network_type, volume_type)

    print("----Initializing the agent...")
    agent_unified_four_legs_three_lanes = MpcAgent(paras, "unified_four_legs_three_lanes")
    agent_unified_four_legs_three_lanes.clear_redundant_gams_files()

    phase_list_multi=[]
    duration_list_multi=[]
    step = 0
    while env_single_intersection.is_active():

        print(f"----Get network state at step {step}")
        network_state = env_single_intersection.get_state_cur_intersection(step)

        if control_type == "multi_scale":
            # print("----Get control commands from the agent")
            (next_global_step_to_re_solve_the_network, phase_list_multi, duration_list_multi, should_update_signal, next_signal_phase, speed_commands) = (
                agent_unified_four_legs_three_lanes.get_control_commands(
                    paras, network_state, step
                )
            )
            env_single_intersection.apply_control_commands(
                should_update_signal, next_signal_phase, speed_commands
            )

        elif control_type == "actuated":
             env_single_intersection.pedestrian_actuation()

            #env_single_intersection.pedestrian_movement_control()
        env_single_intersection.calculate_extra_metrics()
        env_single_intersection.move_one_step_forward()
        step += 1
        print(f"-------------------------------")

    env_single_intersection.close_sumo_simulation()
    env_single_intersection.performance_results_scenario(phase_list_multi, duration_list_multi, network_type, volume_type, control_type, step)
    agent_unified_four_legs_three_lanes.clear_redundant_gams_files()



network_type = "single_intersection"
volume_type = "symmetric"
control_type = "fixed_time"
ped_phasing_val = 'Exclusive' # "Concurrent" or "Exclusive"
pene_value = 1
scenario_base(network_type, volume_type, control_type, ped_phasing_val, pene_value)
"""
parameter_name = "penetration"
values = [0, 0.33, 0.66, 1]
for parameter_value in values:
    scenario(network_type, volume_type, control_type, parameter_name, parameter_value)"
"""