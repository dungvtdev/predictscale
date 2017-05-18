import pprint


def dumps_object(obj):
    print('**************************************'
          '***** object %s ****************************'
          '********************************************' % obj)

    pprint.pprint(vars(obj))
