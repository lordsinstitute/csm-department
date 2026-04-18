# import socket
# print(socket.gethostbyname('controller.us-east.pinecone.io'))


# import os
# # print("Pinecone key:", bool(os.getenv("PINECONE_API_KEY")))


# from pinecone import Pinecone
# pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
# print(pc.describe_index("medical-chatbot-cpu").status)


# import os
# os.environ['PINECONE_BASE_URL'] = 'https://controller.us-east1-gcp.pinecone.io'


# print(os.getenv("PINECONE_API_KEY"))

from pinecone import Pinecone

pc = Pinecone(api_key="pcsk_3qLcpR_M6EiMBwyU4jEh1rrh1CLfAuGFaUGEsL2nefvUChKhU3twbcV8g8DnAk7pc789T1")
index = pc.Index("quickstart")