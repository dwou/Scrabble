
import re # I just learned this so it might be ugly

# Terminology:
# lines = Extracted data lines (see NWL_data.txt)
# POS = Part of speech
# word (base) = Dictionary term, first part of line
# word (root) = Root word from synonyms or pointers
# angle_part / curly_part = part that contains <> or {} in each line
# end part = the [] part with POS and other word forms at the end
# desc = description = part of line between word and end part
# meaning = entire part of line after base word

'''
*** Types of lines (non-exhaustive, there may be mixes of each) ***

# zero derivatives
  AE one [adj]

# one derivative
  AA rough, cindery lava [n AAS]

# 2+ derivaties
  AH {aah=v} [v AHED, AHING, AHS]

# {} (Synonym of another word)
  AD an {advertisement=n} [n ADS]

# <> (form of another word, points to root word)
  AM <be=v> [v]

# / (multiple meanings, 2+)
  OS a bone [n OSSA] / an {esker=n} [n OSAR] / an {orifice=n} [n ORA]

# Multiple parts of speech (from multiple meanings) (compensated for in ^)
   ILL not {well=v} [adj ILLER, ILLEST] / an {evil=n} [n ILLS]

Steps:
1) Extract word and split line into parts for each '/' (alt meaning)
    * WORD description [POS forms]
2) For each meaning:
    * Extract parts, get definitions if necessary, reformat line

There is a major problem with root words having a different meaning than intended,
like ILL (adj) defined from 'WELL' (v) (it's supposed to be WELL (adj)), but this
seems unfixable without removing necessary context in some words.

'''

def remake_desc(meaning):
    POS = re.search(r'\[(.*?)[?:\s|\]]', meaning).group(1)
    endpart = re.search(r'(\[.*?)$', meaning).group(1)
    if ' / ' in meaning:
        meaning_1 = re.search(r'^(.*?)(?=\s/\s|$)', meaning).group(1)
        meanings = (meaning_1,) + tuple(re.findall(r'\s/\s(.*?)(?=\s/\s|$)', line))
        ret_meanings = [ remake_desc(i) for i in meanings ]
        return ret_meanings[0]
    if '{' in meaning: # Synonym
        ''' {} (Synonym of another word)
            AD an {advertisement=n} [n ADS] '''
        root = re.search(r'{(.*?)=', meaning).group(1).upper()
        if root in mentioned_here:
            return meaning
        mentioned_here.append(root)
        root_POS = re.search(r'\[(.*?)[?:\s|\]]', words_and_desc[root]).group(1)
        try:
            root_desc = re.search(r'^(.*?)\s\[', words_and_desc[root]).group(1)
        except:
            root_desc = '(no description)'
        curly_part = re.search(r'{.*?}', meaning).group()
        desc = re.search(r'^(.*?)\s\[', meaning).group(1)
        replace_text = f'{root.upper()} ({root_POS}) {root_desc}' # to replace {} text
        new_desc = f'{desc.replace(curly_part,replace_text)} {endpart}'
    elif '<' in meaning: # Pointer to root word
        root = re.search(r'<(.*?)=', meaning).group(1).upper()
        if root in mentioned_here:
            return root
        mentioned_here.append(meaning)
        root_POS = re.search(r'\[(.*?)[?:\s|\]]', words_and_desc[root]).group(1)
        try:
            root_desc = re.search(r'^(.*?)\s\[', words_and_desc[root]).group(1)
        except:
            root_desc = '(no description)'
        angle_part = re.search(r'<.*?>', meaning).group()
        desc = re.search(r'^(.*?)\s\[', meaning).group(1)
        # After:  a GOVERNOR (n) one that GOVERNS (v) to rule or direct [n GUVS]
        replace_text = f'{root.upper()} ({root_POS}) {root_desc}' # to replace <> text
        new_desc = f'{desc.replace(angle_part,replace_text)} {endpart}'
    else: # done, passes all checks first try
        return meaning
    if ('{' not in new_desc) and ('<' not in new_desc):
        return new_desc
    return remake_desc(new_desc) # New Iteration


if 1:
    # get list of unofficial words / descriptions
    # get the file from idk find it yourself
    # This looks good enough
    # https://github.com/scrabblewords/scrabblewords/blob/main/words/North-American/NSWL2020.txt
    with open("NWL_data.txt","r") as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        lines = [line.strip().replace(' ', '\t', 1) for line in lines]
        for i,line in enumerate(lines):
            if '{ldquo}' in line: # replace this text with ""
                lines[i] = line.replace('{ldquo}','"').replace('{rdquo}','"')
        words_and_desc = { line[:line.find('\t')] : line[line.find('\t')+1:] for line in lines }
        words_newdescs = {}


if 1:
    # Line to word and new description(s)
    with open('outfile.txt','w') as f:
        for line in lines:
            # Capture base word and first meaning
            base,meaning_1 = re.search(r'^(.*?)\s(.*?)(?=\s/\s|$)', line).groups()
            # Captures all additional meanings, if there are any
            meanings = (meaning_1,) + tuple(re.findall(r'\s/\s(.*?)(?=\s/\s|$)', line))

            mentioned_here = [] # to prevent recursion errors
            out_descs = [remake_desc(meaning) for meaning in meanings]
            #for meaning in meanings:
            #    out_descs.append(remake_desc(meaning))
            words_newdescs[base] = tuple(out_descs)
            if '$' in words_newdescs[base]:
                print(base)
                print(words_newdescs[base])
            if len(words_newdescs[base]) >= 4:
                print(base)
                for i,j in enumerate(words_newdescs[base]):
                    print(f'  {i+1}: {j}')
            words_newdescs[base] = [ i for i in words_newdescs[base] ]
            # '$' delimiter ; add breaks for Anki ; must have HTML enabled
            card = base + '$' + '<br>'.join(words_newdescs[base])
            f.write(card+'\n')

if 0:
    for line in lines:
        # Check for lines containing <>
        if '<' in line:
            match = re.search(r'<(.*?)=([\w\s]+)>', line)
            if match:
                word, part_of_speech = match.group(1), match.group(2)
                transformed_line = f"{word.upper()}\t{part_of_speech}. {word_data.get(word, '')}"

        # Check for lines containing {}
        elif '{' in line:
            match = re.search(r'\{(.*?)=([\w\s]+)\}', line)
            if match:
                word, part_of_speech = match.group(1), match.group(2)
                transformed_line = f"{word.upper()}\t{part_of_speech}. {word_data.get(word, '')}"

        # Lines without <> or {}
        else:
            word = re.match(r'(\w+)', line).group(1)
            part_of_speech_match = re.search(r'\[([\w\s]+)\]', line)
            if part_of_speech_match:
                part_of_speech = part_of_speech_match.group(1)
                print(word,part_of_speech)
                transformed_line = f"{word}\tn. {line[line.find(word):].strip()}"
            else:
                transformed_line = f"{word}\tn. {line[line.find(word):].strip()}"
        print(f'Orig:\t{repr(line)}')
        print(f'Trans:\t{repr(transformed_line)}')
        counter += 1
        if counter >= 280:
            break


if 0:
    # create file with words/descriptions by frequency if words are official
    with open('words_desc_sorted.csv','w') as f_out:
        with open('unigram_freq.csv','r') as f_in:
            lines = f_in.readlines()[1:]
            for line in lines:
                word = line[:line.find(',')]
                if word.upper() in words_and_desc:
                    out = f'{word.upper()}\t{words_and_desc[word.upper()].capitalize()}'
                    f_out.write(out)

if 0:
    # just replace first space with \t
    with open('words_desc.csv','w') as f_out:
        for word in words:
            out = f'{word}\t{words_and_desc[word].capitalize()}'
            f_out.write(out)

if 0:
    # replace first space with \t and show alt spelling definition
    with open('words_desc_2.csv','w') as f_out:
        for word in words:
            desc = words_and_desc[word]
            if '=' in desc:
                desc 
            out = f'{word}\t{words_and_desc[word].capitalize()}'
            f_out.write(out)










