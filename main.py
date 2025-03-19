## The entry point of the Multiscale SVCC algorithm.
import traci
from configs.set_parameters import set_parameters
from environment.single_intersection import SingleIntersection
from agent.mpc_agent import MpcAgent
from plots import plots
import scenario

def main(generate, inputs):
    if generate=='result':
        scenario.scenario_base(inputs['network_type'], inputs['volume_type'], inputs['control_type'], inputs['ped_phasing'], inputs['pene_value'])
    elif generate=='plot':
        df = plots.read_results_files('Results/Increase Demand')
        focus_col_list = ['waiting_time', 'queue_length', 'fuel_consumption']
        plots.plot_matrix(df, focus_col_list, 'penetration', export=inputs['export_1'], filename='maxtrix plot-UW intersection-Increase-absolute value.png')
        df_avg = plots.rel_percent_by_fixed_time(df, focus_col_list, ['ped_phasing', 'penetration'])
        plots.plot_matrix(df_avg, focus_col_list, 'penetration', percentage=True, export=inputs['export_2'], filename='maxtrix plot-UW intersection-Increase-percentage.png')
        df.to_csv('Results/UW_Increase.csv')


if __name__ == "__main__":
    # main("single_intersection", "symmetric", "multi_scale")
    # control_type: "multi_scale", "actuated", "fixed_time"
    """
    generate = 'result'
    for control_type in ["actuated", "fixed_time", "multi_scale"]:
        for ped_phasing in ["Exclusive", "Concurrent"]:
            for pene_value in [1, 0.8, 0.5, 0.2]:
                inputs['control_type'] = control_type # "multi_scale", "actuated", "fixed_time"
                inputs['ped_phasing'] = ped_phasing # "Concurrent" or "Exclusive"
                inputs['pene_value'] = pene_value
                main(generate, inputs)

                if ((control_type == "multi_scale") & (ped_phasing == "Exclusive") & (pene_value == 0.2)) \
                    | ((control_type == "multi_scale") & (ped_phasing == "Concurrent") & (pene_value == 0.5)) \
                    :
                    inputs['control_type'] = control_type # "multi_scale", "actuated", "fixed_time"
                    inputs['ped_phasing'] = ped_phasing # "Concurrent" or "Exclusive"
                    inputs['pene_value'] = pene_value
                    main(generate, inputs)
                else:
                    continue
    """
    """
    generate = 'result'
    inputs = {}
    inputs['network_type'] = 'UW_intersection'
    inputs['volume_type'] = "symmetric"
    inputs['control_type'] = 'multi_scale'
    inputs['ped_phasing'] = 'Exclusive'
    inputs['pene_value'] = 0.2
    main(generate, inputs)
    """
    generate = 'plot'
    inputs = {}
    inputs['export_1'] = True
    inputs['export_2'] = True
    main(generate, inputs)