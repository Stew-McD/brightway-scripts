"""
This module is designed to process chemical substances from a CSV file containing 
CAS (Chemical Abstracts Service) numbers. It fetches chemical data using the cirpy 
library, generates chemical structure images using RDKit, and saves the information 
and images to disk.
"""

import os
import shutil
from pathlib import Path
from time import sleep

import cirpy as cp
import pandas as pd
from rdkit import Chem


# Set up file paths and directories
cd = os.path.dirname(os.path.realpath(__file__))
FILE_INPUT = "ecoinvent-310-cutoff_CAS_numbers.csv"
FILE_OUTPUT = FILE_INPUT.replace(".csv", "ANDstructures.csv")
DIR_STRUCTURES = "structures"
DIR_GIT_PAGES = Path(cd).parent.parent / 'Stew-McD.github.io'

# Ensure the structures directory exists
DIR_STRUCTURES = Path(DIR_STRUCTURES)
if not DIR_STRUCTURES.is_dir():
    os.mkdir(DIR_STRUCTURES)
# else:
#     os.system(f"rm {DIR_STRUCTURES}/*")

# Define the fields to resolve for each substance
fields = [
    "iupac_name",
    "smiles",
    "stdinchi",
    "names",
    "formula",
    "mw",
]

# if you just want to use the output file from a previous run to make images, set this to False
RESOLVE = False
if not RESOLVE:
    FILE_INPUT = FILE_OUTPUT

# Set up retry parameters, in case the cirpy API fails
RETRY = True
ATTEMPTS = 5
SLEEP = 2


def resolve_field(x, field):
    """
    Resolve a specific field for a given CAS number using the cirpy library.

    Args:
    x (str): The CAS number of the substance.
    field (str): The specific chemical property to resolve.

    Returns:
    str or None: The resolved property, or None if resolution failed.
    """
    try:
        print(f"Resolving {field} for {x}")
        result = cp.resolve(x, field)
        if field == "stdinchi":
            result = result.replace("InChI=", "")
        if result:
            print(f"\t {str(result)[0:50]}")
        else:
            print("\t ** No result")
        return result
    except Exception as e:
        print(f"\t** Error resolving {field} for {x}: \n\t{e}")
        return None


def get_image(x, font):
    """
    Generate an annotated SVG image of the chemical structure from a SMILES string and save it.

    Args:
    x (dict): A dictionary, row, series, etc. containing chemical properties of the substance.
    font (str): The font style to use in the SVG image.

    Returns:
    None

    Raises:
    Exception: If the SMILES string is missing or if the image generation fails.

    NOTE  Chem.Draw thing seems to only work in interactive terminals, like Jupyter notebooks ipython. There is probably a way to make it work in a script, but I haven't figured it out yet.
    """
    if not x["smiles"]:
        return Exception("No SMILES string")
    try:
        m = Chem.MolFromSmiles(x["smiles"])
        d = Chem.Draw.rdMolDraw2D.MolDraw2DSVG(600, 400)
        o = d.drawOptions()
        if font == '"Comic Neue"':  # unfortunately, comic mode is not working :(
            o.comicMode = True
        d.DrawMolecule(m)
        d.FinishDrawing()
        # Get the SVG text
        text = d.GetDrawingText()
        # Build and append additional text to the SVG
        if "formula" not in x or not x["formula"]:
            x["formula"] = ""
        if "names" not in x or not x["names"]:
            x["names"] = ""
        x.fillna("", inplace=True)

        replacement = (
            f'<text x="20" y="10" font-family={font} font-size="12">CAS:{x["CAS number"]}  ---  MW: {str(x["mw"])}</text>'
            f'<text x="20" y="25" font-family={font} font-size="8">SMILES: {x["smiles"]}</text>'
            f'<text x="20" y="35" font-family={font} font-size="8">Formula: {x["formula"]}</text>'
            f'<text x="20" y="370" font-family={font} font-size="12">ecoinvent: {x["name"]}</text>'
            f'<text x="20" y="385" font-family={font} font-size="12">IUPAC: {x["iupac_name"]}</text>'
            # f'<text x="20" y="395" font-family={font} font-size="2">Synonyms: {x["names"]}</text>'
            "</svg>"
        )
        if text:
            text = text.replace("</svg>", replacement)

        # add rounded mw and CAS number to filename for sorting
        FILE_STRUCTURE = DIR_STRUCTURES / f'{x["mw_round"]}_{x["CAS number"]}.svg'
        # if FILE_STRUCTURE.is_file():
        #     new_filename = str(FILE_STRUCTURE).replace(".svg", f"{x['name'].replace(' ','').split(',')[0]}.svg")
        #     FILE_STRUCTURE.rename(new_filename)
        with open(FILE_STRUCTURE, "w") as f:
            f.write(text)
        return None
    except Exception as e:
        print(f"Error getting image for {x['name']}: {e}")
        with open("error_log.txt", "a") as f:
            f.write(f"{x['name']}: {e}\n")
        return None


def main(FILE_INPUT, FILE_OUTPUT, SLEEP=1):
    """
    Main function to process all CAS numbers in the dataframe to resolve chemical properties and generate images

    Args:
    FILE_INPUT (str): The path to the CSV file containing the CAS numbers.
    FILE_OUTPUT (str): The path to the CSV file to save the processed data.
    SLEEP (int): The number of seconds to wait between each CAS number to avoid overloading the cirpy API.

    Returns:
    None

    Raises:
    None
    """
    # Read the CSV file containing the CAS numbers
    df = pd.read_csv(FILE_INPUT, sep=";")
    output_rows = []
    # Process each row in the dataframe
    for i, row in df.iterrows():
        print(f"\n{i}/{len(df)} - //// Processing: {row['name'][0:50]} ////")
        # Resolve each field for the substance using the cirpy library
        if RESOLVE:
            for field in fields:
                if field not in row or not row[field]:
                    row[field] = resolve_field(row["CAS number"], field)
                    sleep(SLEEP)
            # Get a rounded MW value for the filename (for sorting)
        if row["mw"]:
            try:
                row["mw_round"] = str(int(float(row["mw"]))).zfill(4)
            except Exception as e:
                row["mw_round"] = ""                
        # Generate an image of the chemical structure
        for font in ['"Arial Narrow"']:
            if row["smiles"]:
                get_image(row, font)

        # Append the processed row to the output dataframe
        output_rows.append(row)

    # Save the processed data to a CSV and a pickle file
    df_out = pd.DataFrame(output_rows)
    df_out.to_csv(FILE_OUTPUT, sep=";", index=False)
    df_out.to_pickle(FILE_OUTPUT.replace(".csv", ".pkl"))

    return None


def retry_main_function(FILE_OUTPUT, ATTEMPTS=5, SLEEP=2):
    """
    Sometimes the resolver function has connection errors, so this function can retry the main function to try to fill the gaps

    Args:
    FILE_OUTPUT (str): The path to the CSV file to load and save the processed data.
    ATTEMPTS (int): The number of times to retry the main function.

    Returns:
    None

    Raises:
    Exception: If the main function fails after the specified number of attempts.

    """

    for i in range(ATTEMPTS):
        SLEEP = SLEEP * (i + 1)
        print(f"Retrying ({i+1}/{ATTEMPTS}) with SLEEP = {SLEEP}...")
        try:
            main(FILE_OUTPUT, FILE_OUTPUT, SLEEP)
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    return None


if __name__ == "__main__":
    main(FILE_INPUT, FILE_OUTPUT, SLEEP=1)
    if RETRY:
        retry_main_function(FILE_OUTPUT, ATTEMPTS, SLEEP=2)
    
    # Copy the structure images to the web directory
    if DIR_GIT_PAGES.is_dir():
        shutil.rmtree(DIR_GIT_PAGES / "assets/chemical_structures")
        shutil.copytree(DIR_STRUCTURES, DIR_GIT_PAGES / "assets/chemical_structures")
        print(f"Structure images copied to {DIR_GIT_PAGES / 'assets/chemical_structures'}")
