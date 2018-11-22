
import sys

from src.sparc.ecgtracecreation.datasource import read_data
from src.sparc.ecgtracecreation.datastore import get_complementary_file_name, save_data
from src.sparc.ecgtracecreation.interpolate import evaluate_8x8_grid
from src.sparc.ecgtracecreation.zincmesh import create_mesh


def main():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        data = read_data(file_name)
        if data:
            region, time_sequence = create_mesh(data)
            if region:
                interpolated_data = evaluate_8x8_grid(region, time_sequence)
                if interpolated_data:
                    output_file_name = get_complementary_file_name(file_name)
                    save_data(output_file_name, interpolated_data)
                else:
                    sys.exit(-4)
            else:
                sys.exit(-3)
        else:
            sys.exit(-2)
    else:
        sys.exit(-1)


if __name__ == "__main__":
    main()
