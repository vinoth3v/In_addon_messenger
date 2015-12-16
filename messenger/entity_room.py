
#import In.entity

class Room(In.entity.Entity):
	'''Room Entity class.
	'''
	
	def __init__(self, data = None, items = None, **args):
		
		self.members = []
		
		super().__init__(data, items, **args)
	
	def get_title(self, from_nabar_id):
		# TODO: CACHE IT
		
		if self.title:
			return self.title
			
		if self.type == 'su':
			# set to_nabar_id
			if self.members[0] == from_nabar_id:
				to_nabar_id = self.members[1]
			else:
				to_nabar_id = self.members[0]
			
			nabar = IN.entitier.load_single('Nabar', to_nabar_id)
			if nabar:
				return nabar.name
		
		if self.members:
			members = []
			max_members = 3
			for m in self.members:
				if m != from_nabar_id:
					members.append(m)
					if len(members) >= max_members:
						break
			
			names = []
			nabars = IN.entitier.load_multiple('Nabar', members)
			for n, nabar in nabars.items():
				names.append(nabar.name)
			
			title = ', '.join(names)
			
			if len(self.members) > len(names):
				title += s(' and {num} other(s)', {'num' : str(len(self.members) - len(names))})
			
			return title
			
		return s('Room')
	
	def access(self, op, nabar_id):
		''''''
		
		# TODO: OP based, relation/ban based
		
		if not nabar_id:
			return False
			
		if self.type == 'public':
			return True
		
		if nabar_id in self.members:
			return True
			
		return False
	
@IN.register('Room', type = 'Entitier')
class RoomEntitier(In.entity.EntityEntitier):
	'''Base Room Entitier'''

	# Room needs entity insert/update/delete hooks
	invoke_entity_hook = True

	# load all is very heavy
	entity_load_all = False
	
@IN.register('Room', type = 'Model')
class RoomModel(In.entity.EntityModel):
	'''Room Model'''

	def load_entity_additional_data(self, entity):
		'''load_entity_additional_data'''
		
		# load room members
		try:
			entity.members = []
			
			cursor = IN.db.select({
				'table' : 'message.room_nabar',
				'columns' : ['nabar_id'],
				'where' : [
					['room_id', entity.id],
				]
			}).execute()
			
			if cursor.rowcount == 0:
				return
			rows = cursor.fetchall()
			for row in rows:
				entity.members.append(row['nabar_id'])
				
		except Exception as e:
			IN.logger.debug()
		
@IN.hook
def entity_model():
	return {
		'Room' : {					# entity name
			'table' : {				# table
				'name' : 'room',
				'columns' : {		# table columns / entity attributes
					'id' : {},
					'type' : {},
					'created' : {},
					'status' : {},
					'nabar_id' : {},
					'title' : {},
				},
				'keys' : {
					'primary' : 'id',
				},
			},
		},
	}

@IN.register('Room', type = 'Themer')
class RoomThemer(In.entity.EntityThemer):
	'''Room themer'''

	
	def theme_attributes(self, obj, format, view_mode, args):
		
		obj.css.append('messenger-trigger i-panel i-margin-small-bottom i-margin-small-top i-pointer')
		
		obj.attributes['data-room_id'] = obj.id
		obj.attributes['onclick'] = 'UIkit.offcanvas.hide();'
		super().theme_attributes(obj, format, view_mode, args)
		
	#def theme(self, obj, format, view_mode, args):
		#super().theme(obj, format, view_mode, args)
		

	def theme_process_variables(self, obj, format, view_mode, args):
		super().theme_process_variables(obj, format, view_mode, args)
		
		context = args['context']
		
		#nabar = IN.entitier.load('Nabar', obj.nabar_id)
		
		#args['nabar_name'] = nabar.name
		#args['nabar_id'] = nabar.id
		#args['nabar_picture'] = IN.nabar.nabar_profile_picture_themed(nabar)
		#args['value'] = 'room'
		
		from_nabar_id = context.nabar.id
		
		args['value'] = obj.get_title(from_nabar_id)
		
		# set nabar icon
		if obj.type == 'su':
			
			picture_path = ''
			
			if obj.members[0] == from_nabar_id:
				to_nabar_id = obj.members[1]
			else:
				to_nabar_id = obj.members[0]
			
			nabar = IN.entitier.load_single('Nabar', to_nabar_id)
			
			if nabar:
				picture_path = IN.nabar.nabar_profile_picture_uri(nabar)
			
			if picture_path:
				args['nabar_picture'] = picture_path.join(('<img src="', '" class="" />'))
			else:
				args['nabar_picture'] = '<i class="i-icon-user i-icon-large"></i>'
			
		else:
			args['nabar_picture'] = '<i class="i-icon-group i-icon-large"></i>'
		
		args['nabar_picture'] = args['nabar_picture'].join(('<div class="nabar-picture i-float-left i-width i-margin i-margin-small-right nabar-picture-xsmall">', '</div>'))
		
