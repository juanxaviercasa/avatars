with open('viralforge/overlay_profiles.py', 'r', encoding='utf-8') as f:
    content = f.read()

with open('scripts/reactivo_profile_snippet.py', 'r', encoding='utf-8') as f:
    snippet = f.read()

dispatch_marker = 'def build_overlays_for_video('
parts = content.split(dispatch_marker)
if len(parts) == 2:
    new_content = parts[0] + snippet + '\n' + dispatch_marker + parts[1]
    
    dispatch_case = "    elif 'REACTIVO' in stem_upper or 'LIMITANTE' in stem_upper:\n        return build_overlays_reactivo_limitante(workdir, dur, category_tag, clean_hook, custom_cta_phrase, cta_target)\n"
    target_branch = "    elif \"FXAD4126\" in stem_upper:"
    if target_branch in new_content:
        new_content = new_content.replace(target_branch, dispatch_case + target_branch)
        with open('viralforge/overlay_profiles.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('SUCCESS')
    else:
        print('FXAD4126 branch not found')
else:
    print('build_overlays_for_video not found')
