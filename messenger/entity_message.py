
#import In.entity

class Message(In.entity.Entity):
	'''Message Entity class.
	'''
	
	room_id = None
	
	def __init__(self, data = None, items = None, **args):
		
		super().__init__(data, items, **args)
		

@IN.register('Message', type = 'Entitier')
class MessageEntitier(In.entity.EntityEntitier):
	'''Base Message Entitier'''

	# Message needs entity insert/update/delete hooks
	invoke_entity_hook = True

	# load all is very heavy
	entity_load_all = False
	
@IN.register('Message', type = 'Model')
class MessageModel(In.entity.EntityModel):
	'''Message Model'''


@IN.hook
def entity_model():
	return {
		'Message' : {						# entity name
			'table' : {				# table
				'name' : 'message',
				'columns' : {		# table columns / entity attributes
					'id' : {},
					'type' : {},
					'created' : {},
					'status' : {},
					'nabar_id' : {},
					'room_id' : {},
				},
				'keys' : {
					'primary' : 'id',
				},
			},
		},
	}

@IN.register('Message', type = 'Themer')
class MessageThemer(In.entity.EntityThemer):
	'''Message themer'''

	def theme_attributes(self, obj, format, view_mode, args):
		
		obj.attributes['data-id'] = obj.id # needed for js
		super().theme_attributes(obj, format, view_mode, args)

	def theme(self, obj, format, view_mode, args):
		super().theme(obj, format, view_mode, args)
		

	def theme_process_variables(self, obj, format, view_mode, args):
		super().theme_process_variables(obj, format, view_mode, args)
		
		nabar = IN.entitier.load('Nabar', obj.nabar_id)
		
		args['nabar_name'] = nabar.name
		args['nabar_id'] = nabar.id
		args['nabar_picture'] = IN.nabar.nabar_profile_picture_themed(nabar)
	
		
		args['created'] = In.core.util.format_datetime_friendly(obj.created)
		
