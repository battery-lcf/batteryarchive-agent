# batteryarchive agent

The battery archive agent contains all the tools needed to get a site like www.batteryarchive.org going:

1. Redash interface optimized to display battery data
2. JSON API to connect to external data sources
3. Sample data that you can use to learn how to import your data
4. Import and Jupyter Notebook scripts

## Requirements 

The batteryarchive agent needs a Linux or MAC computer with 8 GB of RAM and the latest version of Docker and Docker-compose.

## Installation steps

To install the battery-archive agent follow these steps:

1. git clone https://github.com/battery-lcf/batteryarchive-agent
2. cd batteryarchive-agent
3. ./bin/gen_env
4. ./bin/setup5. ./bin/start

The script gen_env generates the information required to access the Postgres database where your battery data is installed. You can see what is in the env file by running more env.

When you run the setup script, you will be asked to enter an email and password. These credentials are needed to access the Redash front web page.

After the start script completes, you will be given the URLs to access the various components of the batteryarchive agent.

If you have questions or comments, please contact us at info@batteryarchive.org