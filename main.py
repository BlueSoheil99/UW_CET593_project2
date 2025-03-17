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
        df = plots.read_results_files('Results')
        focus_col_list = ['waiting_time', 'queue_length', 'fuel_consumption']
        plots.plot_matrix(df, focus_col_list, 'penetration', export=inputs['export_1'], filename='maxtrix plot-UW intersection-absolute value.png')
        df_avg = plots.norm_by_fixed_time(df, focus_col_list, ['ped_phasing', 'penetration'])
        plots.plot_matrix(df_avg, focus_col_list, 'penetration', percentage=True, export=inputs['export_2'], filename='maxtrix plot-UW intersection-percentage.png')
        df.to_csv('Results/UW_normal.csv')


if __name__ == "__main__":
    # main("single_intersection", "symmetric", "multi_scale")
    # control_type: "multi_scale", "actuated", "fixed_time"

    """
    generate = 'result'
    inputs = {}
    inputs['network_type'] = 'UW_intersection'
    inputs['volume_type'] = "symmetric"
    for control_type in ["multi_scale", "actuated", "fixed_time"]:
        for ped_phasing in ["Exclusive", "Concurrent"]:
            for pene_value in [1, 0.8, 0.5, 0.2]:
                if ((control_type == "multi_scale") & (ped_phasing == "Exclusive")) \
                    | ((control_type == "multi_scale") & (ped_phasing == "Concurrent") & (pene_value != 0.2)):
                    continue
                else:
                    inputs['control_type'] = control_type # "multi_scale", "actuated", "fixed_time"
                    inputs['ped_phasing'] = ped_phasing # "Concurrent" or "Exclusive"
                    inputs['pene_value'] = pene_value
                    main(generate, inputs)
    """
    generate = 'plot'
    inputs = {}
    inputs['export_1'] = True
    inputs['export_2'] = True
    main(generate, inputs)