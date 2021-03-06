import unittest
import yota
from yota.validators import *
from yota.nodes import *
from yota.exceptions import *


class TestValidators(unittest.TestCase):
    """ Testing for all our built-in validators """

    def run_check(self, values, validator):
        """ a utility method to run the check by hand. Pass it key value data
        like what a post object would have and it builds the args for your
        check accordingly """
        args = []
        for key, val in values.items():
            args.append(EntryNode(_attr_name=key, data=val))

        c = Check(validator, *args)
        c.resolved = True
        c.validate()
        ret = []
        for a in args:
            if len(a.errors) > 0:
                ret.append(a)

        return ret

    def test_min_required(self):
        """ min validator testing, pos and neg """
        meth = MinLengthValidator(5, message="Darn")

        errors = self.run_check({'t':'short'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t':'shor'}, meth)
        assert(len(errors) > 0)

    def test_max_required(self):
        """ max validator testing, pos and neg """
        meth = MaxLengthValidator(5, message="Darn")

        errors = self.run_check({'t':'shor'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t':'toolong'}, meth)
        assert(len(errors) > 0)

    def test_regex_valid(self):
        """ regex validator testing, pos and neg """
        meth = RegexValidator(regex='^[a-z]*$', message='darn')

        errors = self.run_check({'t':'asdlkfdfsljgdlkfj'}, meth)
        assert(len(errors) == 0)

        # negative
        errors = self.run_check({'t':'123sdflkns'}, meth)
        assert(len(errors) > 0)

    def test_email(self):
        """ email validator testing, all branches """
        meth = EmailValidator(message="Darn")

        errors = self.run_check({'t': 'm@testing.com'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t': 'toolong'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': 'm@t%.com'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': u'm@t\x80%.com'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': u'@$%^%&^*m@t\x80%.com'}, meth)
        assert(len(errors) > 0)
        errors = self.run_check({'t': u'm@\xc3.com'}, meth)
        assert(len(errors) == 0)

    def test_required(self):
        """ required validator """
        meth = RequiredValidator(message="Darn")

        errors = self.run_check({'t': 'toolong'}, meth)
        assert(len(errors) == 0)
        errors = self.run_check({'t': ''}, meth)
        assert(len(errors) > 0)

class TestCheck(unittest.TestCase):
    def test_key_access_exception(self):
        """ Proper raising of access exception when missing a required piece of
        data """
        class TForm(yota.Form):
            t = EntryNode()
            _t_valid = yota.Check(RequiredValidator(message="Darn"), 't')

        test = TForm()
        self.assertRaises(DataAccessException, test._gen_validate, {})
