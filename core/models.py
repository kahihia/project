from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

#----------------------------------------------------------------------------------------------------------
#             Class Identity defines role in application
#----------------------------------------------------------------------------------------------------------
class Identity(models.Model):
    title = models.CharField(max_length=128, unique=True)
    member = models.ManyToManyField('self', through='Participant', symmetrical=False, related_name='i2i')

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class Participant defines relationships between two Identities
#----------------------------------------------------------------------------------------------------------
class Participant(models.Model):
    title = models.CharField(max_length=128, unique=True)
    community = models.ForeignKey(Identity, related_name='comm2part')
    part = models.ForeignKey(Identity, related_name='part2comm')

    date_from = models.DateField(default=0)
    date_to = models.DateField(default=0)

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class Dictionary defines dictionary for attributes in application
#----------------------------------------------------------------------------------------------------------
class Dictionary(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title



    def getSlotsList(self):
        '''
        Return queryset of Slots  associated with dictionary
        '''
        slots = Slot.objects.filter(dict=self.id)
        return slots

    def createSlot(self, title):
        '''
        Create new Slot
        '''
        slot = Slot(title=title, dict=self)
        slot.save()

    def updateSlot(self,oldTitle,newTitle):
        '''
        Update Slot
        '''
        Slot.objects.filter(dict__id=self.id, title=oldTitle).update(title=newTitle)


    def deleteSlot(self,slotTitle):
        '''
        Delete slot
        '''
        slot = Slot.objects.get(dict=self.id,title=slotTitle)
        slot.delete()







#----------------------------------------------------------------------------------------------------------
#             Class Slot defines row in dictionary for attributes in application
#----------------------------------------------------------------------------------------------------------
class Slot(models.Model):
    title = models.CharField(max_length=128)
    dict = models.ForeignKey(Dictionary, related_name='slot')

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ("title", "dict")



#----------------------------------------------------------------------------------------------------------
#             Class Attribute defines attributes for Item in application
#----------------------------------------------------------------------------------------------------------
class Attribute(models.Model):
    title = models.CharField(max_length=128)
    type = models.CharField(max_length=3)
    dict = models.ForeignKey(Dictionary, related_name='attr', null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ("title", "type")


    def __str__(self):
        return self.title









#----------------------------------------------------------------------------------------------------------
#             Class Permission defines operations for particular Identity
#----------------------------------------------------------------------------------------------------------
class Permission(models.Model):
    title = models.CharField(max_length=128)

    role = models.ForeignKey(Identity, related_name='identity')

    create_flag = models.BooleanField(default=False)
    read_flag = models.BooleanField(default=True)
    update_flag = models.BooleanField(default=False)
    delete_flag = models.BooleanField(default=False)
    get_flag = models.BooleanField(default=True)
    run_flag = models.BooleanField(default=False)

    class Meta:
        unique_together = ("title", "role")

    def __str__(self):
        return self.title

    def get_perm_for_identity(self):
        return self.create_flag, self.read_flag, self.update_flag, self.delete_flag, self.get_flag, self.run_flag

#----------------------------------------------------------------------------------------------------------
#             Class State defines current state for particular item instance
#----------------------------------------------------------------------------------------------------------
class State(models.Model):
    title = models.CharField(max_length=128, unique=True)
    perm = models.ForeignKey(Permission, related_name='state')

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class Process defines process which is attached to particular Item
#----------------------------------------------------------------------------------------------------------
class Process(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class Action defines member of the process, which is attached to particular Item
#----------------------------------------------------------------------------------------------------------
class Action(models.Model):
    title = models.CharField(max_length=128, unique=True)
    papa = models.ForeignKey(Process, related_name='action')
    child_proc = models.ForeignKey(Process, related_name='start_node', default=0) #handle to child process

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class ActionPath defines connection between two Actions in Process
#----------------------------------------------------------------------------------------------------------
class ActionPath(models.Model):
    title = models.CharField(max_length=128, unique=True)
    source = models.ForeignKey(Action, related_name='act2path')
    target = models.ForeignKey(Action, related_name='path2act')

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class Item defines basic primitive for application objects
#----------------------------------------------------------------------------------------------------------
class Item(models.Model):
    title = models.CharField(max_length=128, unique=True)
    member = models.ManyToManyField('self', through='Relationship', symmetrical=False, null=True, blank=True)
    attr = models.ManyToManyField(Attribute, related_name='item')
    status = models.ForeignKey(State, null=True, blank=True)
    proc = models.ForeignKey(Process, null=True, blank=True)

    class Meta:
        permissions = (
            ("can_get", "Can get Item"),
            ("can_run", "Can run Procedure"),
        )

    #def __init__(self, name):
    #   title = name



    def __str__(self):
        return self.title


    def createAndSetAttribute(self, title, type, dict=None, start_date=None, end_date=None):
        '''
        Method create new Attribute and set it to specific item
        '''
        attribute = Attribute(title=title, type=type, dict=dict, start_date=start_date, end_date=end_date)
        attribute.save()
        item = Item.objects.get(id=self.id)
        attribute.item.add(item)

    def setAttribute(self, title, type):
        '''
        Method set existing  attribute to specific item , if attribute is not found return False
        '''
        attribute = self.getAttribute(title, type)
        if attribute != False:
            item = Item.objects.get(id=self.id)
            attribute.item.add(item)
        else:
            return False

    def getAttribute(self, title, type):
        '''
        Method return attribute by title and type , if is not found return False
        '''
        try:
          attribute = Attribute.objects.get(title=title, type=type)
        except ObjectDoesNotExist:
            return False

        return attribute



    @staticmethod
    def getItemsAttributesValues(attr, items):
        '''
           Return values of attribute list in items list
        '''
        values = Value.objects.filter(attr__title__in=attr, item__in=items).order_by("item")
        values = list(values.values("title", "attr__title", "item__title", "item"))


        valuesAttribute = {}

        for valuesDict in values:
            if valuesDict['item'] not in valuesAttribute:
                valuesAttribute[valuesDict['item']] = {'title': [valuesDict['item__title']]}

            if valuesDict['attr__title'] not in valuesAttribute[valuesDict['item']]:
                valuesAttribute[valuesDict['item']][valuesDict['attr__title']] = []

            valuesAttribute[valuesDict['item']][valuesDict['attr__title']].append(valuesDict['title'])

        return valuesAttribute


    def getAttributeValues(self, *attr):
        '''
           Return values of attribute list in specific Item
        '''

        values = Value.objects.filter(attr__title__in=attr, item=self.id)
        values = list(values.values("title", "attr__title", "item__title", "item"))


        valuesAttribute = {}

        for valuesDict in values:
            if valuesDict['item'] not in valuesAttribute:
                valuesAttribute[valuesDict['item']] = {'title': [valuesDict['item__title']]}

            if valuesDict['attr__title'] not in valuesAttribute[valuesDict['item']]:
                valuesAttribute[valuesDict['item']][valuesDict['attr__title']] = []

            valuesAttribute[valuesDict['item']][valuesDict['attr__title']].append(valuesDict['title'])

        return valuesAttribute










    @transaction.atomic
    def setAttributeValue(self, attrWithValues):
        '''
            Set values for attributes (mass)
        '''
        if not isinstance(attrWithValues, dict) or not attrWithValues :
            raise ValueError

        queries = []
        bulkInsert = []
        attributes = attrWithValues.keys()
        existsAttributes = Attribute.objects.filter(title__in=attributes).all()

        if len(existsAttributes) != len(attrWithValues):
            raise ValueError

        for attr in attributes:
            attributeObj = existsAttributes.get(title=attr)
            dictID = attributeObj.dict_id
            attr = attributeObj.title
            values = attrWithValues[attr]

            if not isinstance(values, list):
                values = [values]

            for value in values:

                if dictID is None:
                    bulkInsert.append(Value(title=value, item=self, attr=attributeObj))
                else:
                    #security
                    dictID = int(dictID)
                    valueID = int(value)

                    #check if dictionary slot exists for this dictionary - creating conditions
                    queries.append('Q(dict=' + str(dictID) + ', pk=' + str(valueID) + ')')

        #check if dictionary slot exists for this dictionary - using conditions
        filter_or = ' | '.join(queries)
        attributesValue = Slot.objects.filter(eval(filter_or)).values('dict__attr__title','title','dict__attr__id')

        if len(attributesValue) < len(queries):
            raise ValueError

        for attribute in attributesValue:
            value = attribute['title']
            attrID = attribute['dict__attr__id']
            attributeObj = existsAttributes.get(pk=attrID)

            bulkInsert.append(Value(title=value, item=self, attr=attributeObj))

        sid = transaction.savepoint()

        try:
            Value.objects.filter(attr__title__in=attributes, item=self.id).delete()
            Value.objects.bulk_create(bulkInsert)
        except Exception:
            transaction.savepoint_rollback(sid)

            raise Exception
        else:
            transaction.savepoint_commit(sid)

        return True

'''    def create(self):
        if self.status.perm.create_flag:
            return self.objects.create(s    elf)
        else:
            return 'You can\'t create Item. Not enough rights.'
'''
#----------------------------------------------------------------------------------------------------------
#             Class Relationship defines relationships between two Items
#----------------------------------------------------------------------------------------------------------
class Relationship(models.Model):
    title = models.CharField(max_length=128, unique=True)
    parent = models.ForeignKey(Item, related_name='p2c')
    child = models.ForeignKey(Item, related_name='c2p')

    qty = models.FloatField()
    create_date = models.DateField(auto_now_add=True)
    create_user = models.ForeignKey(Identity)

    class Meta:
        unique_together = ("parent", "child")

    def __str__(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#             Class Value defines value for particular Attribute-Item relationship
#----------------------------------------------------------------------------------------------------------
class Value(models.Model):
    title = models.TextField()
    attr = models.ForeignKey(Attribute, related_name='attr2value')
    item = models.ForeignKey(Item, related_name='item2value')


#    class Meta:
        #db_tablespace = 'core_values'
    class Meta:
        unique_together = ("title", "attr","item")
        db_tablespace = 'TPP_CORE_VALUES'



    def __str__(self):
        return self.title

    def get(self):
        return self.title

#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------
#             Signal receivers
#----------------------------------------------------------------------------------------------------------
@receiver(pre_save, sender=Item)
def item_create_callback(sender, **kwargs):
    print("Item creation: check authority!")
