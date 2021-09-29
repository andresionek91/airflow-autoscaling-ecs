import json
import pandas as pd


def do_something_to_json(raw_json, output_json):
    pass


def pandas_process_CSV(input, output, fields):
    with open(input, 'r', encoding='utf-8') as input_file:
        df = pd.read_csv(input_file)

        # do something to dataframe
        df = df.groupby(fields) \
                .agg({
                        fields[0]:'nunique'
                    })

        # save as csv to specified desination
        df.to_csv(output) # only use index=False for dataframes that do not have grouped/aggregate data
        input_file.close()



def process_awhere_JSON(input, output):
    with open(input, 'r', encoding='utf-8') as input_file, open(output, 'w', encoding='utf-8') as output_file:
        line = input_file.readline()
        while line:
            # TODO: process row somehow
            # json_format = {}
            row = json.loads(line)
            if row:
                output_file.write(json.dumps(row) + '\n')
            line = input_file.readline()
        output_file.close()
        input_file.close()