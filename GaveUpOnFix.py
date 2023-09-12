
import re # I just learned this so it might be ugly


it's driving me mad, I give up

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

def get_POS(meaning):
    return re.search(r'\[(.*?)[?:\s|\]]', meaning).group(1)

def get_endpart(meaning):
    return re.search(r'(\[.*?)$', meaning).group(1)

def get_nested_word(meaning):
    if '{' in meaning or '<' in meaning:
        return re.search(r'[{<](.*?)=', meaning).group(1).upper()

def get_nested_POS(meaning):
    if '{' in meaning or '<' in meaning:
        return re.search(r'=(.*?)[}>]', meaning).group(1)

def print_nested_data(meaning):
    nested_word = get_nested_word(meaning)
    nested_pos = get_nested_POS(meaning)
    print(f'Nested: {nested_pos} {nested_word} (depth {get_depth(nested_word,nested_pos)}) {words_meanings[nested_word][nested_pos]}')

def get_desc(meaning): # doesn't fill in {} <>
    if desc := re.search(r'^(.*?)\[', meaning).group(1).strip():
        return desc
    return '(no description)'


def remake_desc2(meaning): # multiple meanings not allowed; non-recursive; for new code
    endpart = get_endpart(meaning)
    #print(len(words_pos_desc.keys()))
    if '{' in meaning or '<' in meaning:
        POS = get_POS(meaning)
        root = re.search(r'[{<](.*?)=', meaning).group(1).upper() # For either {} or <>
        #if root in mentioned_here:
        #    return root
        #mentioned_here.append(meaning)
        root_POS = get_POS(words_and_desc[root])
        if word=='ACICULA':
            pass#print(root_POS, root, meaning)
        works=0
        for i in range(10):
            try:
                root_meaning = completed_word_pos_indx[root][root_POS][i]
                works=1
            except:
                pass#print(i,word,'failed')
        if not works:
            0/0
        root_desc = get_desc(root_meaning)
        #print(root_POS, root, meaning)
        desc = re.search(r'^(.*?)\s\[', meaning).group(1)
        replace_text = f'{root.upper()} ({root_POS}) {root_desc}' # to replace {}/<> text
        
        if '{' in meaning: # Synonym
            curly_angle_part = re.search(r'{.*?}', meaning).group()
        else: # Pointer to root word
            curly_angle_part = re.search(r'<.*?>', meaning).group()
        
        new_desc = f'{desc.replace(curly_angle_part,replace_text)} {endpart}'
    else: # No change
        return get_desc(meaning) + ' ' + endpart # accounts for (no description)
    return new_desc


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
        # { WORD : raw_meanings_str }
        words_and_desc = { line[:line.find('\t')] : line[line.find('\t')+1:] for line in lines }
        
        words_newdescs = {} # OLD
        # { WORD : { POS:(meanings) } } parsed
        words_pos_desc = {}


if 1:
    # Get words, POS, pos_indx by depth and put in here
    # depth_map will be figured out befored meanings are fully parsed
    depth_map_nomeaning = { } # { 1 : { (word,POS) } } see below
    depth_map = { } # { 1 : { (word,POS,pos_indx) } } see below

    # This is the important one
    words_meanings = { } # { word : { POS : [meanings], ... }, ... }
    to_parse = set() # set { (word,POS,mpos_index), } don't do meaning yet

    def get_depth(word,POS): # Only gets POS of [word][POS][0] *** see notes
        # returns 0 if not in depth_map_nomeaning
        for i in range(len(depth_map_nomeaning.keys())):
            if (word,POS) in depth_map_nomeaning[i+1]:
                return i+1
        return 0

    def print_words_meanings(word):
        print(word)
        for POS in words_meanings[word]:
            print(' ',POS)
            for meaning in words_meanings[word][POS]:
                print('   ',meaning)
    
    # First, create dict of words and meanings (unparsed) (works?)

    # Example:
    # FLY
    #   adj
    #     {clever=adj} [adj FLIER, FLIEST]
    #   v
    #     to hit a ball high into the air in baseball [v FLIED, FLIES, FLYING]
    #     to move through the air [v FLEW, FLIES, FLOWN, FLYING]


    for line in lines:
        base,meaning_1 = re.search(r'^(.*?)\s(.*?)(?=\s/\s|$)', line).groups()
        meanings = (meaning_1,) + tuple(re.findall(r'\s/\s(.*?)(?=\s/\s|$)', line))
        #print(base)
        words_meanings[base] = {}
        for meaning in meanings:
            POS = get_POS(meaning)
            if POS not in words_meanings[base]:
                words_meanings[base][POS] = []
            words_meanings[base][POS].append(meaning)
        for POS in words_meanings[base]:
            #print(' ',POS)
            for POS_indx in range(len(words_meanings[base][POS])):
                pass#print('   ',words_meanings[base][POS][POS_indx])
        POS_counts = {}
        for i in meanings:
            POS = get_POS(i)
            if POS not in POS_counts:
                POS_counts[POS] = 0
            POS_counts[POS] += 1
            to_parse.add( (base,POS,POS_counts[POS]-1) )
            #if POS not in words_meanings[base]:
            #    words_meanings[base][POS] = []
            #words_meanings[base][POS].append()
            #for POS_indx in range(len(words_meanings[base][POS])):
            #    if base=='ABLE':
            #        print((base,POS,POS_indx))
            #    to_parse.add( (base,POS,POS_indx) )
        #if base=='ABLE':
        #    print(sorted(to_parse))
    #print_words_meanings('FLY')

    print(len(to_parse))

    # Second, get all 1-depth meanings
    depth_map[1] = set()
    depth_map_nomeaning[1] = set()
    to_removes = set()
    for i in list(to_parse):
        if i[0] == 'ACICULA':
            print(i)
    for group in sorted(to_parse):
        #print(1,group)
        word, POS, pos_index = group
        #print_words_meanings(word)
        #print(3,(word,POS,pos_index))
        meaning = words_meanings[word][POS][pos_index]
        if word == 'ACICULA':
            print(group, meaning)
        if '{' not in meaning and '<' not in meaning:
            if word == 'ACICULA':
                print('PASSES')
            # passes
            #to_parse.remove(group)
            to_removes.add(group)
            #print(f'Adding {[word,POS,meaning]}')
            #if pos_index:
            #    print(word,pos_index,meaning)
            depth_map[1].add((word,POS,pos_index))
            depth_map_nomeaning[1].add((word,POS))
    for group in to_removes:
        to_parse.remove(group)
    print('Depth: ', get_depth('ABLE','adj'))
    
    print(len(to_parse))


    # Third get all n-depth meanings
    for depth in range(2,7):
        print(f'\n   ****Starting depth {depth} with {len(to_parse)} words left****\n')
        depth_map[depth] = set()
        depth_map_nomeaning[depth] = set()
            #input(to_parse)
        '''
            for group in sorted(to_parse):
                print('\n')
                word, POS, pos_index = group
                meaning = words_meanings[word][POS][pos_index]
                print_words_meanings(word)
                nested_POS = get_nested_POS(meaning)
                nested_word = get_nested_word(meaning)
                print(f'meaning: {meaning}')
                print(f'nested: {nested_POS} {nested_word} (depth {get_depth(nested_word,nested_POS)})')
                group = (nested_word, nested_POS, 0)
        '''
        for group in sorted(to_parse):
            word, POS, pos_index = group
            meaning = words_meanings[word][POS][pos_index]
            nested_word = get_nested_word(meaning)
            nested_POS = get_nested_POS(meaning)
            if word=='ACICULA':
                print(word, POS, pos_index)
                print(meaning,nested_word,nested_POS)
            if get_depth(nested_word,nested_POS) == depth - 1: # passes
                to_parse.remove(group)
                depth_map[depth].add((word,POS,meaning))
                depth_map_nomeaning[depth].add((word,POS))
                if word=='ACICULA':
                    print('passed', depth, (word,POS) in depth_map_nomeaning[depth])


    print(words_meanings['ACICULA'])
    print(('ACICULA','n') in depth_map_nomeaning[1])
    print('ACICULUM' in depth_map_nomeaning[1])
    print(len(depth_map_nomeaning[1]))
    #print(depth_map_nomeaning[1])
    #print(words_pos_desc[('ACICULA','n')])

    # Fourth, parse and add all words. Some words don't work: word to point to is ambiguous -> causes problems with depth
    completed_word_pos_indx = {}
    for i in range(3):
        for depth in range(1,7):
            for word,POS in sorted(depth_map_nomeaning[depth]):
                for pos_indx in range(2):
                    try:
                        meaning = words_meanings[word][POS][pos_indx]
                        
                        if depth >= 1:
                            pass#print()
                            #print(depth,word,meaning)
                            #print('Word depth',get_depth(word,POS))
                            #print(get_desc(meaning).capitalize())
                        new_meaning = remake_desc2(meaning)
                        if depth >= 1:
                            pass#print(new_meaning)
                        if word not in completed_word_pos_indx:
                            completed_word_pos_indx[word] = { }
                        if POS not in completed_word_pos_indx[word]:
                            completed_word_pos_indx[word][POS] = []
                        completed_word_pos_indx[word][POS][pos_indx] = new_meaning
                        break
                    except:
                        pass#print(word,'broken')
    print(len(list(completed_word_pos_indx.keys())))
    print([i for i in completed_word_pos_indx if i not in words_and_desc ])

    '''
    # Fifth, parse all the meanings
    for depth in range(2,7):
        for word,POS in sorted(depth_map_nomeaning[depth]):
            meaning = words_meanings[word][POS][0]
            print()
            print(word,meaning)
            print(get_desc(meaning).capitalize())
            print(remake_desc2(meaning))
    '''
    


    # IGNORE THIS FOR NOW
    # Fifth, get rid of the stragglers (circular dependencies)
    # Let's not put them in depth_map and depth_map_nomeaning
    for group in sorted(to_parse):
        word, POS, pos_index = group
        meaning = words_meanings[word][POS][pos_index]
        to_write = word + '$' + None
        to_parse.remove(group)
        
        #card = base + '$' + '<br>'.join(words_newdescs[base]) + '\n'

