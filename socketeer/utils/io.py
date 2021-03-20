import socket

"""
Open a socket conn on given host, port and send the provided payload

Await the buffered response and return it
"""
def broadcast(host, port, payload):
  s = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
  )

  s.connect((host, port))
  s.send(payload)

  response = s.recv(1024)
  s.close()

  return response