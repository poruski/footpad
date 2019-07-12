import inspector
import argparse
import os

def processFile(urlFile):
    if os.path.exists(urlFile):
        valid = []
        urlData = open(urlFile).read().splitlines()
        for item in urlData:
            if 'http://' not in item and 'https://' not in item:
                print('ERROR! {} is an invalid url! Skipping...'.format(item))
            else:
                valid.append(item)
        if len(valid) == 0:
            print('ERROR! No valid URLs were provided!')
        else:
            inspector.initializeScan(valid)
    else:
        print('ERROR! Invalid URL file provided')

def processSingle(url):
    if 'http://' not in url and 'https://' not in url:
        print('ERROR! {} is an invalid url! Skipping...'.format(url))
    else:
        inspector.scanBroker().initializeScan([url])
    

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Footpad Web Inspector BETA')
    parser.add_argument('--url',help='Single url to scan (example: https://github.com)')
    parser.add_argument('--file',help='Full path to file of urls to scan')
    args = parser.parse_args()
    if args.file == None and args.url == None:
        parser.print_help()
    else:
        if args.file != None and args.url == None:
            processFile(args.file)
        elif args.file == None and args.url != None:
            processSingle(args.url)
        else:
            print('Please provide either a single url or a file of urls to scan')
            
        

