import socket
import subprocess
import sys
import time

from os.path import relpath, isfile

from .cli import get_args

from ..utils.log import log

from ..utils.io import broadcast

from ..utils.constants import \
  ROOT_SCRIPTS_DIR as root, \
  UPDATE_REPO as script, \
  COMMIT_SHA as commit, \
  INTERVAL as interval

"""
Poll the target repository at *interval* of seconds

Check for new commits to target repository and notify dispatch srv of changes
by way of new commit SHAs

Broadcast notifications to dispatch srv with said commit SHA to initialize tests
"""
def poll ():
  args = get_args()
  host, port = args.dispatch.split(':')
  repo = args.repository

  script_path = f'{root}/{script}'

  while True:
    # execute shell script to pull repository, check for new commits
    # persists commit SHA in tmp file in cwd if applicable
    try:
      subprocess.check_output([
        script_path, 
        repo
      ])

    except OSError as ex:
      if ex.errno == 2:
        raise FileNotFoundError(f'{relpath(script_path)} was not found')
      raise Exception(
        'An I/O error occurred ' + 
        ex
      )

    except subprocess.CalledProcessError as ex:
      raise Exception(
        'Unable to update and observe repository ' + 
        ex.output.decode('utf-8', errors='ignore')
      )

    if isfile(commit):
      # repository state has changed
      try:
        # ping dispatch srv
        response = broadcast(
          host, 
          int(port),
          'STATUS:'
        )
      
      except socket.error as ex:
        raise ConnectionError(
          'Unable to ping dispatch srv ' + 
          ex
        )
      
      if response == 'OK':
        # dispatch srv is live
        commit_sha = ''
        with open(commit, 'r') as f:
          commit_sha = f.readline()
        # initialize tests
        response = broadcast(
          host,
          int(port),
          'DISPATCH:' + commit_sha
        )
        
        if response != 'OK':
          raise ConnectionError(
            'Unable to broadcast to dispatch srv ' + 
            response
          )

        log(
          level='success', 
          message=f'Dispatch directive successfully broadcast'
        )
      
      else:
        raise ConnectionError(
          'Unable to connect to dispatch srv ' +
          response
        )
    
    time.sleep(interval)
   


