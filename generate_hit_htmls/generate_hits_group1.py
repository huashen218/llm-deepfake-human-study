import os
import re
import pandas as pd


def create_dir(folder_path):
    r"""Create folder dirs when paths not exist.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)



def read_data(data_path, format = "csv"):
    r"""This is the function to read the data.

    Args:
        data_path (`str`): 
            path of data file.
        format ('str):
            format of the data file. Currently only includes 'csv'.
    Returns:
        generations (`List[str]`): List of all generated paragraphs.
        prompts (`List[str]`):     List of all prompts.
        labels (`List[str]`):      List of all true labels.

    """

    if format == "csv":
        df = pd.read_csv(data_path)
        # print(df)
        generations = df['textA'].tolist()
        prompts = df['prompt'].tolist()
        labels = df['label'].tolist()

    return generations, prompts, labels




def generate_one_hit(html_template_file, generations, prompts, labels, output_html_folder_path, hit_index):

    with open(html_template_file, "r", encoding='utf-8') as f:
        html_content= f.read()


    prompt_keys = ["a1-prompt", "a2-prompt", "a3-prompt", "a4-prompt", "a5-prompt"]
    paragraph1_keys = ["a1-paragraph1", "a2-paragraph1", "a3-paragraph1", "a4-paragraph1", "a5-paragraph1"]
    paragraph2_keys = ["a1-paragraph2", "a2-paragraph2", "a3-paragraph2", "a4-paragraph2", "a5-paragraph2"]
    paragraph3_keys = ["a1-paragraph3", "a2-paragraph3", "a3-paragraph3", "a4-paragraph3", "a5-paragraph3"]
    label_keys = ["a1-label", "a2-label", "a3-label", "a4-label", "a5-label"]

    for i in range(len(generations)):

        paragraph1 = re.search('<p>  <mark>(.+?)</mark>  </p>', generations[i]).group(1)
        paragraph2 = re.search('<p>  <mark2>(.+?)</mark2>  </p>', generations[i]).group(1)
        paragraph3 = re.search('<p>  <mark3>(.+?)</mark3>  </p>', generations[i]).group(1)

        html_content = html_content.replace("{{"+str(prompt_keys[i])+"}}", prompts[i])
        html_content = html_content.replace("{{"+str(paragraph1_keys[i])+"}}", paragraph1)
        html_content = html_content.replace("{{"+str(paragraph2_keys[i])+"}}", paragraph2)
        html_content = html_content.replace("{{"+str(paragraph3_keys[i])+"}}", paragraph3)
        html_content = html_content.replace("{{"+str(label_keys[i])+"}}", labels[i])


    with open(os.path.join(output_html_folder_path, f"{hit_index}.html"), "w") as file:
        file.write(html_content)




def main():

    ### Define paths: html_template, output_folder, data_file_path.
    group = "group1"
    # version = "v_write"

    versions = ["v_write", "v_select"]

    for version in versions:
            
        root_dir = os.path.dirname(os.path.realpath(__file__))
        html_template_file = os.path.join(root_dir, f"group1_template_{version}.html") if group == "group1" else os.path.join(root_dir, "group2_template.html") 

        output_html_folder_path = os.path.join(root_dir, f"htmls/{group}/{version}")
        create_dir(output_html_folder_path)

        data_path = os.path.join(root_dir, "data_gpt2_trial.csv")

        ### Read data
        generations, prompts, labels = read_data(data_path, format = "csv")


        ### Generate each HIT (has n articles)
        n = 5
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(generations), n):
            hit_index = f"{group}_hit{i}"
            generate_one_hit(html_template_file, generations[i:i + n], prompts[i:i + n], labels[i:i + n],  output_html_folder_path, hit_index)



if __name__ == "__main__":
    main()



