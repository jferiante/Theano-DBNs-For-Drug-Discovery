import generate_folds, os, sys



fold_paths = [
    "./folds/DUD-E",
    "./folds/MUV",
    "./folds/Tox21",
    "./folds/PCBA",
    ]



def get_fold_path(data_type):

    if(data_type == 'DUD-E'):
        return fold_paths[0]

    if(data_type == 'MUV'):
        return fold_paths[1]

    if(data_type == 'Tox21'):
        return fold_paths[2]

    if(data_type == 'PCBA'):
        return fold_paths[3]

    raise ValueError('data_type does not exist:' + str(data_type))



def get_target(fname, data_type):
    return generate_folds.get_target(fname, data_type)



def parse_line(line, data_type):

    # row format: [hash_id, is_active, native_id, fold, bitstring]
    parts = line.rstrip('\n').split(r' ')
    hash_id = parts[0]
    is_active = parts[1]
    native_id = parts[2]
    fold = parts[3]
    bitstring = parts[4]

    return fold, [bitstring, is_active]



def build_targets(fold_path, data_type):

    # init targets
    targets = {}
    for dir_name, sub, files in os.walk(fold_path):
        for fname in files:
            if fname.startswith('.'):
                # ignore system files
                pass
            else:
                target = get_target(fname, data_type)
                targets[target] = []
                # print "file:" + fname + ", target:" + target

        for fname in files:
            if fname.startswith('.'):
                # ignore system files
                pass
            else:
                target = get_target(fname, data_type)
                targets[target].append(fname)
                # print "file:" + fname + ", target:" + target
    
    return targets



def get_folds(data_type):
    fold_path = get_fold_path(data_type)
    targets = build_targets(fold_path, data_type)

    print "Found " + str(len(targets)) + " targets for " + data_type

    # store folds by target
    all_folds = {}
    for target, fnames in targets.iteritems():
        # generate a fold set fo reach target
        folds = {}
        for i in range(5):
            # don't forget -- we are using strings & not integer keys!!!
            folds[i] = []

        #fnames contains all files for this target
        for fname in fnames:
            row = []
            with open(fold_path + '/' + fname) as f:
                lines = f.readlines()
                for line in lines:
                    # put each row in it's respective fold
                    fold, row = parse_line(line, data_type)
                    folds[int(fold)].append(row)

        # add the folds to our target
        # print 'target: ' + target
        # print len(folds)
        all_folds[target] =  folds

    """ Debug """
    # print "length of all folds"
    # print len(folds)
    # print "length of respective folds"
    # print len(folds['0'])
    # print len(folds['1'])
    # print len(folds['2'])
    # print len(folds['3'])
    # print len(folds['4'])

    return all_folds



def tox21():
    # get our 5x folds...
    all_folds = get_folds('Tox21')

    for target, folds in all_folds.iteritems():
        # lets try a generic dataset with just 1 fold
        data = []
        for i in range(len(folds)):
            data += folds[i]

        print 'Running logistic regression for target: ' + target

        



def main(args):
    # generate DUDE-E folds
    # dud_e()
    # muv()
    # pcba()
    tox21()


if __name__ == "__main__":
    main(sys.argv)


