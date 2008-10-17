"""
Text based serializers.
"""

import simplejson

from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.model.policy import Policy # XXX might be able to be rid of this


class Serialization(SerializationInterface):

    def list_recipes(self, recipes):
        """
        Create a JSON list of recipe names from
        the provided recipes.
        """
        return simplejson.dumps([recipe.name for recipe in recipes])

    def list_bags(self, bags):
        """
        Create a JSON list of bag names from the
        provided bags.
        """
        return simplejson.dumps([bag.name for bag in bags])

    def list_tiddlers(self, bag):
        """
        List the tiddlers in a bag as JSON.
        The format is a list of dicts in
        the form described by self._tiddler_dict.
        """
        return simplejson.dumps([self._tiddler_dict(tiddler) for tiddler in bag.list_tiddlers()])

    def recipe_as(self, recipe):
        """
        A recipe as a JSON dictionary.
        """
        policy = recipe.policy
        policy_dict = {}
        for key in ['owner', 'read', 'write', 'create', 'delete', 'manage']:
            policy_dict[key] = getattr(policy, key)
        return simplejson.dumps(dict(desc=recipe.desc, policy=policy_dict, recipe=recipe.get_recipe()))

    def as_recipe(self, recipe, input_string):
        """
        Turn a JSON dictionary into a Recipe
        if it is in the proper form. Include
        the policy.
        """
        info = simplejson.loads(input_string)
        try:
            recipe.set_recipe(info['recipe'])
            recipe.desc = info['desc']
            if info['policy']:
                recipe.policy = Policy()
                for key, value in info['policy'].items():
                    recipe.policy.__setattr__(key, value)
        except KeyError:
            pass
        return recipe

    def bag_as(self, bag):
        """
        Create a JSON dictionary representing
        a Bag and Policy.
        """
        policy = bag.policy
        policy_dict = {}
        for key in ['owner', 'read', 'write', 'create', 'delete', 'manage']:
            policy_dict[key] = getattr(policy, key)
        info = dict(policy=policy_dict, desc=bag.desc)
        return simplejson.dumps(info)

    def as_bag(self, bag, input_string):
        """
        Turn a JSON string into a bag.
        """
        info = simplejson.loads(input_string)
        if info['policy']:
            bag.policy = Policy()
            for key, value in info['policy'].items():
                bag.policy.__setattr__(key, value)
        bag.desc = info.get('desc', '')
        return bag

    def tiddler_as(self, tiddler):
        """
        Create a JSON dictionary representing
        a tiddler, as described by _tiddler_dict
        plus the text of the tiddler.
        """
        tiddler_dict = self._tiddler_dict(tiddler)
        tiddler_dict['text'] = tiddler.text

        return simplejson.dumps(tiddler_dict)

    def as_tiddler(self, tiddler, input_string):
        """
        Turn a JSON dictionary into a Tiddler.
        """
        dict_from_input = simplejson.loads(input_string)
        for key, value in dict_from_input.iteritems():
            if value:
                setattr(tiddler, key, value)

        return tiddler

    def _tiddler_dict(self, tiddler):
        """
        Select fields from a tiddler to create
        a dictonary.
        """
        unwanted_keys = ['text', 'recipe', 'store']
        wanted_keys = [attribute for attribute in tiddler.__slots__ if attribute not in unwanted_keys]
        wanted_info = {}
        for attribute in wanted_keys:
            wanted_info[attribute] = getattr(tiddler, attribute)
        return dict(wanted_info)
