import os
import getopt
import sys

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hs:p:", ["script=","path="])
    except getopt.GetoptError:
        print('run as: python3 data_import_agent.py -s <script> -p <path>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run as: python3 data_import_agent.py -s <script> -p <path>')
            sys.exit()
        elif opt in ("-s", "--script"):
            script = arg
            if script == 'li-cell':
                script = 'li_data_import_agent'
            elif script == 'flow-cell':
                script = 'flow_data_import_agent'
            elif script == 'li-module':
                script = 'module_data_import_agent'
            elif script == 'flow-stack':
                script = 'flow_data_import_agent'
        elif opt in ("-p", "--path"):
            path = arg

    os.system('python3 ' + script + '.py ' + path)
    
if __name__ == '__main__':
    main(sys.argv[1:])
    

