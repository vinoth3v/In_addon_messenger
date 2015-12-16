

class MessageTrigger(HTMLObject):
	'''MessageTrigger.
	'''
	
	nabar = None
	room = None
	

@IN.register('MessageTrigger', type = 'Themer')
class MessageTriggerThemer(HTMLObjectThemer):
	'''MessageTrigger themer'''

	def theme_attributes(self, obj, format, view_mode, args):
		
		obj.css.append('messenger-trigger i-panel i-margin-small-bottom i-margin-small-top i-pointer')
		super().theme_attributes(obj, format, view_mode, args)


	def theme_process_variables(self, obj, format, view_mode, args):
		super().theme_process_variables(obj, format, view_mode, args)
		
		context = args['context']
		
		if obj.nabar:
			# title
			args['value'] = obj.nabar.name
			
			picture_path = IN.nabar.nabar_profile_picture_uri(obj.nabar)
			
			if picture_path:
				args['nabar_picture'] = picture_path.join(('<img src="', '" class="" />'))
			else:
				args['nabar_picture'] = '<i class="i-icon-user i-icon-large"></i>'
			
		elif obj.room:
			
			from_nabar_id = context.nabar.id
			# title
			args['value'] = obj.get_title(from_nabar_id)
			
			room = obj.room
		
			# set nabar icon
			if room.type == 'su':
				
				picture_path = ''
				
				if room.members[0] == from_nabar_id:
					to_nabar_id = room.members[1]
				else:
					to_nabar_id = room.members[0]
				
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
			

