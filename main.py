import sys
import argparse
import configparser
import logging
import os.path
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient


def listb(args, containerclient):


    """ Cette fonction liste le contenu du blob 
        Terminal : py main.py list """

    logging.debug(f"Compte {config['storage']['account']}")
    logging.debug(f"Conteneur {config['storage']['container']}")
    logging.info(f"Connexion ok")
    logging.info(f"Affichage de la liste du conteneur {config['storage']['container']}")
    blob_list=containerclient.list_blobs()
    for blob in blob_list:
        print(blob.name)


def upload(cible, blobclient):


    """ Cette fonction permet d'envoyer des fichiers vers le
        blob en lui indiquant leur chemin.
        Ecrase le fichier s'il existe déjà dans le conteneur
        Terminal : python main.py upload 'chemin d'accès avec nom du/des fichier'  """


    logging.debug(f"Compte {config['storage']['account']}")
    logging.debug(f"Conteneur {config['storage']['container']}")
    logging.info("Connexion réussie")
    with open(cible, "rb") as f:
        logging.warning(f"Uploading {cible} to container, erasing if already exists")
        blobclient.upload_blob(f)


def download(filename, dl_folder, blobclient):


    """ Cette fonction permet de télécharger depuis le conteneur, en précisant 
        le nom du fichier à télécharger 
        Terminal : py download hello.txt  """

    logging.debug(f"Compte {config['storage']['account']}")
    logging.debug(f"Conteneur {config['storage']['container']}")
    logging.info("Connexion réussie")
    with open(os.path.join(dl_folder,filename), "wb") as my_blob:
        logging.info(f"Downloading {filename}")
        blob_data=blobclient.download_blob()
        logging.warning(f"Downloading blob object into local file")
        blob_data.readinto(my_blob)


def main(args,config):


    """ Cette fonction est lancé au démarrage du script
    Fais le liens avec le fichier config.ini
    En fonction de l'argument, appel la fonction associée' """


    logging.warning(f"Reading the associated configuration file (config.ini)")   
    blobclient=BlobServiceClient(
        f"https://{config['storage']['account']}.blob.core.windows.net",
        config["storage"]["key"],
        logging_enable=True)
    containerclient=blobclient.get_container_client(config["storage"]["container"])
    if args.action=="list":
        return listb(args, containerclient)
    else:
        if args.action=="upload":
            blobclient=containerclient.get_blob_client(os.path.basename(args.cible))
            return upload(args.cible, blobclient)
        elif args.action=="download":
            blobclient=containerclient.get_blob_client(os.path.basename(args.remote))
            return download(args.remote, config["general"]["restoredir"], blobclient)
    

if __name__=="__main__":
    parser=argparse.ArgumentParser("Logiciel d'archivage de documents")
    parser.add_argument("-cfg",default="config.ini",help="chemin du fichier de configuration")
    parser.add_argument("-lvl",default="info",help="niveau de log")
    subparsers=parser.add_subparsers(dest="action",help="type d'operation")
    subparsers.required=True
    
    parser_s=subparsers.add_parser("upload")
    parser_s.add_argument("cible",help="fichier à envoyer")

    parser_r=subparsers.add_parser("download")
    parser_r.add_argument("remote",help="nom du fichier à télécharger")
    parser_r=subparsers.add_parser("list")

    args=parser.parse_args()

    #erreur dans logging.warning : on a la fonction au lieu de l'entier
    loglevels={
        "debug":logging.DEBUG,
        "info":logging.INFO, 
        "warning":logging.WARNING, 
        "error":logging.ERROR, 
        "critical":logging.CRITICAL
        }
    print(loglevels[args.lvl.lower()])
    logging.basicConfig(level=loglevels[args.lvl.lower()])

    config=configparser.ConfigParser()
    config.read(args.cfg)

    sys.exit(main(args,config))