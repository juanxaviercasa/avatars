"""Import a reviewed script over authenticated SSH; never start a render."""
import json
import sys
import re
from .db import store
from .models import Persona,Product,Script,Variant


def import_draft(payload: dict) -> dict:
    allowed={'id','product_id','persona_id','script'}
    if set(payload)!=allowed:
        raise ValueError('Unexpected draft fields')
    if not isinstance(payload['id'],str) or not re.fullmatch(r'var_[A-Za-z0-9_-]{1,80}',payload['id']):
        raise ValueError('Invalid variant identifier')
    if not store().get('personas',payload['persona_id'],Persona) or not store().get('products',payload['product_id'],Product):
        raise ValueError('Product and persona must already exist on Oracle')
    script=Script.model_validate(payload['script'])
    if not 1<=len(script.beats)<=8 or sum(len(b.text.split()) for b in script.beats)>150:
        raise ValueError('Script exceeds limits')
    v=Variant(id=payload['id'],product_id=payload['product_id'],persona_id=payload['persona_id'],script=script,status='queued')
    old=store().get('variants',v.id,Variant)
    if old:
        if old.product_id!=v.product_id or old.persona_id!=v.persona_id or old.script!=v.script:
            raise ValueError('Draft ID conflict')
    else:
        store().put('variants',v)
    return {'variant_id':v.id,'imported':True,'render_started':False}


if __name__=='__main__':
    raw=sys.stdin.buffer.read(64001)
    if len(raw)>64000:
        raise ValueError('Payload exceeds limit')
    print(json.dumps(import_draft(json.loads(raw))))
