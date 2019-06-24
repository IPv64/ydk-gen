""" 
Test cases for YDK entity_diff.


"""

from __future__ import print_function

import unittest

from ydk.types import entity_to_dict, entity_diff

from ydk.models.ydktest import ydktest_sanity as ysanity

# from test_utils import enable_logging, print_entity, print_data_node


def check_empty_str_value(v):
    if isinstance(v, str) and v.__len__() == 0:
        v = 'exists'
    return v


def print_dictionary(legend, ent_dict, key_width=70):
    print("\n------> DICTIONARY%s:" % legend)
    for n, v in sorted(ent_dict.items()):
        print("%s: %s" % (n.rjust(key_width), check_empty_str_value(v)))


def print_diffs(diff, key_width=70):
    print("\n------> DIFFS:")
    for key in diff:
        value = diff[key]
        print("%s: %s vs %s" % (key.rjust(key_width), check_empty_str_value(value[0]), check_empty_str_value(value[1])))


class EntityDiffTest(unittest.TestCase):

    def test_entity_diff_two_key(self):
        runner = ysanity.Runner()
        l_1 = ysanity.Runner.TwoKeyList()
        l_2 = ysanity.Runner.TwoKeyList()
        l_1.first, l_2.first = 'f1', 'f2'
        l_1.second, l_2.second = 11, 22
        l_1.property, l_2.property = '82', '83'
        runner.two_key_list.extend([l_1, l_2])
        
        ent_dict = entity_to_dict(runner)
        self.assertEqual(len(ent_dict), 4)
        print_dictionary('-LEFT', ent_dict)

        runner2 = ysanity.Runner()
        l_1, l_2 = ysanity.Runner.TwoKeyList(), ysanity.Runner.TwoKeyList()
        l_1.first, l_2.first = 'f1', 'f2'
        l_1.second, l_2.second = 11, 22
        l_1.property, l_2.property = '82', '83'
        runner2.two_key_list.extend([l_1, l_2])

        diff = entity_diff(runner, runner2)
        self.assertEqual(len(diff), 0)

        l_1.property = '83'
        print_dictionary('-RIGHT', entity_to_dict(runner2))
        diff = entity_diff(runner, runner2)
        self.assertEqual(len(diff), 1)
        print_diffs(diff)

    def test_entity_diff_two_key_not_equal(self):
        runner = ysanity.Runner()
        l_1, l_2 = ysanity.Runner.TwoKeyList(), ysanity.Runner.TwoKeyList()
        l_1.first, l_2.first = 'f1', 'f2'
        l_1.second, l_2.second = 11, 22
        l_1.property, l_2.property = '82', '83'
        runner.two_key_list.extend([l_1, l_2])

        ent_dict = entity_to_dict(runner)
        self.assertEqual(len(ent_dict), 4)
        print_dictionary('-LEFT', ent_dict)

        runner3 = ysanity.Runner()
        l_1, l_2 = ysanity.Runner.TwoKeyList(), ysanity.Runner.TwoKeyList()
        l_1.first, l_2.first = 'f1', 'f3'
        l_1.second, l_2.second = 11, 22
        l_1.property, l_2.property = '82', '84'
        runner3.two_key_list.extend([l_1, l_2])

        ent_dict = entity_to_dict(runner3)
        self.assertEqual(len(ent_dict), 4)
        print_dictionary('-RIGHT', ent_dict)

        diff = entity_diff(runner, runner3)
        self.assertEqual(len(diff), 2)
        print_diffs(diff)

    def test_entity_to_dict_aug_onelist(self):
        runner = ysanity.Runner()
        e_1 = ysanity.Runner.OneList.OneAugList.Ldata()
        e_2 = ysanity.Runner.OneList.OneAugList.Ldata()
        e_1.number = 1
        e_1.name = "e_1.name"
        e_2.number = 2
        e_2.name = "e_2.name"
        runner.one_list.one_aug_list.ldata.extend([e_1, e_2])
        runner.one_list.one_aug_list.enabled = True

        ent_dict = entity_to_dict(runner)
        self.assertEqual(len(ent_dict), 5)
        print_dictionary('', ent_dict, 60)

    def test_entity_to_dict_enum_leaflist(self):
        runner = ysanity.Runner()
        runner.ytypes.built_in_t.enum_llist.append(ysanity.YdkEnumTestEnum.local)
        runner.ytypes.built_in_t.enum_llist.append(ysanity.YdkEnumTestEnum.remote)

        ent_dict = entity_to_dict(runner)
        self.assertEqual(len(ent_dict), 2)
        print_dictionary('', ent_dict, 50)

    def test_entity_diff_number_leaf(self):
        runner1 = ysanity.Runner()
        runner1.ytypes.built_in_t.number8 = 23

        ent_dict = entity_to_dict(runner1)
        self.assertEqual(len(ent_dict), 1)
        print_dictionary('-LEFT', ent_dict, 50)

        runner2 = ysanity.Runner()

        ent_dict = entity_to_dict(runner2)
        self.assertEqual(len(ent_dict), 0)
        print_dictionary('-RIGHT', ent_dict, 50)

        diff = entity_diff(runner1, runner2)
        self.assertEqual(len(diff), 1)
        print_diffs(diff, 50)

    def test_entity_to_dict_presence(self):
        runner = ysanity.Runner()
        runner.runner_2 = ysanity.Runner.Runner2()
        runner.runner_2.some_leaf = 'some-leaf'

        ent_dict = entity_to_dict(runner)
        self.assertEqual(len(ent_dict), 2)
        print_dictionary('-LEFT', ent_dict, 40)

        runner_ = ysanity.Runner()
        ent_dict = entity_to_dict(runner_)
        self.assertEqual(len(ent_dict), 0)
        print_dictionary('-RIGHT', ent_dict, 40)

        diff = entity_diff(runner, runner_)
        self.assertEqual(len(diff), 1)
        print_diffs(diff, 40)

    def test_entity_diff_two_level_list(self):
        r_1 = ysanity.Runner()
        e_1, e_2 = ysanity.Runner.TwoList.Ldata(), ysanity.Runner.TwoList.Ldata()
        e_11, e_12 = ysanity.Runner.TwoList.Ldata.Subl1(), ysanity.Runner.TwoList.Ldata.Subl1()
        e_1.number = 21
        e_1.name = 'runner:twolist:ldata['+str(e_1.number)+']:name'
        e_11.number = 211
        e_11.name = 'runner:twolist:ldata['+str(e_1.number)+']:subl1['+str(e_11.number)+']:name'
        e_12.number = 212
        e_12.name = 'runner:twolist:ldata['+str(e_1.number)+']:subl1['+str(e_12.number)+']:name'
        e_1.subl1.append(e_11)
        e_1.subl1.append(e_12)
        e_21, e_22 = ysanity.Runner.TwoList.Ldata.Subl1(), ysanity.Runner.TwoList.Ldata.Subl1()
        e_2.number = 22
        e_2.name = 'runner:twolist:ldata['+str(e_2.number)+']:name'
        e_21.number = 221
        e_21.name = 'runner:twolist:ldata['+str(e_2.number)+']:subl1['+str(e_21.number)+']:name'
        e_22.number = 222
        e_22.name = 'runner:twolist:ldata['+str(e_2.number)+']:subl1['+str(e_22.number)+']:name'
        e_2.subl1.append(e_21)
        e_2.subl1.append(e_22)
        r_1.two_list.ldata.append(e_1)
        r_1.two_list.ldata.append(e_2)

        ent_dict = entity_to_dict(r_1)
        self.assertEqual(len(ent_dict), 12)
        print_dictionary('-LEFT', ent_dict, 80)

        r_2 = ysanity.Runner()
        e_1, e_2 = ysanity.Runner.TwoList.Ldata(), ysanity.Runner.TwoList.Ldata()
        e_11, e_12 = ysanity.Runner.TwoList.Ldata.Subl1(), ysanity.Runner.TwoList.Ldata.Subl1()
        e_1.number = 21
        e_1.name = 'runner:twolist:ldata['+str(e_1.number)+']:name'
        e_11.number = 211
        e_11.name = 'runner:twolist:ldata['+str(e_1.number)+']:subl1['+str(e_11.number)+']:name'
        e_12.number = 212
        e_12.name = 'runner:twolist:ldata['+str(e_1.number)+']:subl1['+str(e_12.number)+']:name'
        e_1.subl1.append(e_11)
        e_1.subl1.append(e_12)
        r_2.two_list.ldata.append(e_1)

        ent_dict = entity_to_dict(r_2)
        self.assertEqual(len(ent_dict), 6)
        print_dictionary('-RIGHT', ent_dict, 80)

        diff = entity_diff(r_1, r_2)
        self.assertEqual(len(diff), 1)
        print_diffs(diff, 50)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    testloader = unittest.TestLoader()
    testnames = testloader.getTestCaseNames(EntityDiffTest)
    for name in testnames:
        suite.addTest(EntityDiffTest(name))
    ret = not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
