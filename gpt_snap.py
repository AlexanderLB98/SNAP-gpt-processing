import os
import subprocess
import argparse
import yaml
from glob import glob
import pandas as pd

def run_command(cmd):
    """Ejecuta un comando y maneja los errores."""
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"Comando ejecutado con éxito: {cmd}")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")
        raise
    except Exception as e:
        print(e)
        raise

def resample_image(image, config, gpt_path="gpt"):
    """Remuestrea la imagen."""
    
    input_path = os.path.join(config["image_folder"], image)
    output_path = os.path.join(config["output_folder"], image, "resampled")
    
    # cmd = f"{gpt_path} Resample -PtargetResolution=10 -t {output_file}/resampled {input_file}"
    cmd = f"{gpt_path} Resample -PtargetResolution=10 -t {output_path} {input_path}"
    run_command(cmd)


def apply_c2rcc(image, config, gpt_path="gpt"):
    """Aplica la corrección atmosférica c2rcc."""
    
    # output_directory = image.split("/resampled.dim")[0]
    
    source = os.path.join(config["output_folder"], image, "resampled.dim")
    output_directory = os.path.join(config["output_folder"], image, "c2rcc")
    
    cmd = f"{gpt_path} c2rcc.msi -SsourceProduct={source} -t {output_directory} -PnetSet='C2X-Nets' -PoutputAsRrs=true"
    run_command(cmd)

    
def apply_pixex(image, config, gpt_path="gpt"):
    """Aplica PixEx para extraer datos del punto."""
    
    #output_file_prefix = config["pixex"]["output_prefix"]
    output_file_prefix = 'mi_extraction'
    coordinates_path = config["pixex"]["coordinates_file"]
    
    input_file = os.path.join(config["output_folder"], image, "c2rcc.dim")
    output_file = os.path.join(config["output_folder"], image)
    
    # cmd = f"{gpt_path} PixEx -PcenterLatitude={pin_lat} -PcenterLongitude={pin_lon} -PextractWidth=1 -PextractHeight=1 -t {output_file} {input_file}"
    
    # gpt PixEx -PwindowSize=3 -PcoordinatesFile=coordinates/coordinates.txt -PsourceProductPaths=output/S2B_MSIL1C_20230709T104629_N0509_R051_T30TXL_20230709T125343.SAFE/c2rcc.dim -PoutputDir=output/S2B_MSIL1C_20230709T104629_N0509_R051_T30TXL_20230709T125343.SAFE/pixex -PoutputFilePrefix=extraction
    
    print("------------------------------------")
    print(coordinates_path)
    print(os.path.exists(coordinates_path))
    print(input_file)
    print(os.path.exists(input_file))
    print("------------------------------------")
    
    #cmd = f"gpt PixEx -PwindowSize=3 -PcoordinatesFile={coordinates_path} -PsourceProductPaths={input_file}  -t {output_file} -PoutputFilePrefix={output_file_prefix}"
    
    # This one works in the other folder
    cmd = f"gpt PixEx -PwindowSize=3 -PcoordinatesFile={coordinates_path} -PsourceProductPaths={input_file} -PoutputDir={output_file} -PoutputFilePrefix={output_file_prefix}"
    
    run_command(cmd)

    
def read_measurement_files(root_directory="output"):
    # Buscar todos los archivos que terminen en '_measurements.txt'
    pattern = os.path.join(root_directory, '**', '*_measurements.txt')
    files = glob(pattern, recursive=True)
    
    # Inicializar una lista para almacenar los DataFrames
    dfs = []
    
    for file in files:
        try:
            # Leer el archivo en un DataFrame, saltando las primeras filas
            df = pd.read_csv(file, sep='\t', skiprows=6)
            
            # Agregar el DataFrame a la lista
            dfs.append(df)
            
            print(f"Archivo {file} leído con éxito.")
        
        except Exception as e:
            print(f"Error al leer el archivo {file}: {e}")
    
    # Concatenar todos los DataFrames en uno solo
    all_data = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    
    return all_data



def process_image(image: str, config):
    """Procesa la imagen utilizando comandos directos de SNAP GPT."""
    try:
        if image.endswith("/"):
            image = image.split("/")[-2]
    
        # case_name = image
        
        # print(case_name)
        print(image)
        
        output_folder = config["output_folder"]        # output
        os.makedirs(output_folder, exist_ok=True)
        
        output = os.path.join(output_folder, image)    # Specific image: output/imageX
        os.makedirs(output, exist_ok=True)

        resample_image(image=image, config=config)
        
        apply_c2rcc(image=image, config=config)
        # apply_c2rcc(input_file=os.path.join(output, "resampled.dim"), output_file=output_folder)
        
        apply_pixex(image=image, config=config)
        # apply_pixex(input_file=os.path.join(output, "c2rcc.dim"), output_file=output, coordinates_path = "coordinates.txt")
        
        # return df
        
        
        
    except Exception as e:
        print(f"Error processing {image}: {e}")


def main():
        
    # Initialize the ArgumentParser
    # parser = argparse.ArgumentParser(description="A program to demonstrate optional positional arguments.")

    # Define a required positional argument 'required_arg'
    # parser.add_argument("input_file", type=str, help="This argument is required")

    # Parse the arguments
    # args = parser.parse_args()
    
    
    
    # input_file = args.input_file
    config_file = "config.yaml"
    
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        
    print(config)
    
    input_folder = config["image_folder"]
    
    
    
    for image in os.listdir(input_folder):
        process_image(image=image, config=config)
        
    df_all_images = read_measurement_files()
    df_all_images.to_csv("results.csv", sep=";")

    
if __name__ == "__main__":
    main()