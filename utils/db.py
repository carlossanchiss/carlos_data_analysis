
import os
from supabase import create_client

def sb():
    url=os.environ['SUPABASE_URL']
    key=os.environ['SUPABASE_SERVICE_KEY']
    return create_client(url, key)
