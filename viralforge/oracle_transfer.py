"""Private transfer from operator machine to the existing Oracle generator."""
import argparse
import json
import subprocess
from .config import settings
from .db import store
from .models import Variant


def push_draft(variant_id: str) -> dict:
    variant=store().get('variants',variant_id,Variant)
    if not variant:
        raise ValueError('Unknown local variant')
    payload={key:getattr(variant,key) for key in ('id','product_id','persona_id')}
    payload['script']=variant.script.model_dump()
    remote='cd /opt/viralforge/releases/20261030-connections && env VF_DATA_DIR=/opt/viralforge/data .venv/bin/python -m viralforge.oracle_import'
    result=subprocess.run(['ssh','-T','-i',str(settings.ssh_key_path),'-o','BatchMode=yes',
        '-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','ubuntu@'+settings.oracle_host,remote],
        input=json.dumps(payload),text=True,encoding='utf-8',capture_output=True,timeout=30,
        creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if result.returncode:
        raise RuntimeError('Oracle import failed; confirm product and persona IDs exist there')
    return json.loads(result.stdout)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('variant_id')
    args=parser.parse_args()
    print(json.dumps(push_draft(args.variant_id)))
