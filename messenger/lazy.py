import json
from messenger.page.friend_list import message_friends_init_lister

class MessageListLazy(In.core.lazy.HTMLObjectLazy):
	'''list of comments'''

	def __init__(self, data = None, items = None, **args):

		super().__init__(data, items, **args)

		# always set new id
		self.id = 'MessageListLazy'
		
		context = IN.context
		if context.request.ajax_lazy:
			
			db = IN.db
			connection = db.connection

			nabar_id = context.nabar.id
			
			if not nabar_id:
				return
				
			#query = IN.db.select({
				#'table' : ['message.message_nabar', 'mn'],
				#'columns' : ['r.id'],
				#'join' : [
					#['join', 'message.message', 'm', [
						#['mn.message_id = m.id']
					#]],
					#['join', 'message.room', 'r', [
						#['m.room_id = r.id']
					#]],
				#],
				#'where' : [
					#['mn.nabar_id', nabar_id],
					#['mn.status', '>', 0],
					#['m.status', '>', 0],
				#],
				#'order' : {'m.created' : 'desc'},
				#'group' : ['r.id']
			#})
			
			#cursor = query.execute()
			
			cursor = IN.db.execute('''select id from 
				(
				SELECT distinct on(r.id) r.id, m.created
				FROM message.message_nabar mn  
				join message.message m ON (mn.message_id = m.id)  
				join message.room r ON (m.room_id = r.id) 
				WHERE (mn.nabar_id = %(nabar_id)s) 
				AND (mn.status > 0) AND (m.status > 0) 
				) sub order by created desc limit 20''', {
					'nabar_id' : nabar_id
				}
			)
			if cursor.rowcount > 0:
				
				weight = 0
				
				ids = [row['id'] for row in cursor]
				
				entities = IN.entitier.load_multiple('Room', ids)
				
				for id in ids:
					if id in entities:
						room = entities[id]
						
						obj = ThemeArgs(room, {
							'view_mode' : 'nav',
							'weight' : weight
						})
						
						weight += 1
						
						self.add(obj)
					
					#remaining = total - limit
					#if remaining > 0 and  last_id > 0:
						#self.add('TextDiv', {
							#'id' : '_'.join(('more-commens', parent_entity_type, str(parent_entity_id), str(self.parent_id))),
							#'value' : str(remaining) + ' more comments',
							#'css' : ['ajax i-text-center pointer i-panel-box i-panel-box-primary'],
							#'attributes' : {
								#'data-href' : ''.join(('/comment/more/!Content/', str(parent_entity_id), '/', str(last_id), '/', str(self.parent_id)))
							#},
							#'weight' : -1
						#})

		

@IN.register('MessageListLazy', type = 'Themer')
class MessageListLazyThemer(In.core.lazy.HTMLObjectLazyThemer):
	'''lazy themer'''

	def theme_attributes(self, obj, format, view_mode, args):
		
		obj.css.append('i-nav i-nav-offcanvas')
		obj.lazy_args['type'] = obj.__type__
		
		json_args = ''
		try:
			json_args = json.dumps(obj.lazy_args, skipkeys = True, ensure_ascii = False)
		except Exception as e:
			print(9999999999, obj.lazy_args, obj.__type__)
			raise e
			
		obj.attributes['data-args'] = json_args
		return super().theme_attributes(obj, format, view_mode, args)




class FriendListLazy(In.core.lazy.HTMLObjectLazy):
	'''list of Friends'''

	def __init__(self, data = None, items = None, **args):

		super().__init__(data, items, **args)

		# always set new id
		self.id = 'FriendListLazy'
		
		context = IN.context
		if context.request.ajax_lazy:

			nabar_id = context.nabar.id
			
			if not nabar_id:
				return
			
			message_friends_init_lister(context, self)

		

@IN.register('FriendListLazy', type = 'Themer')
class FriendListLazyThemer(In.core.lazy.HTMLObjectLazyThemer):
	'''lazy themer'''

	def theme_attributes(self, obj, format, view_mode, args):
		
		#obj.css.append('i-nav i-nav-offcanvas')
		obj.lazy_args['type'] = obj.__type__
		
		json_args = ''
		try:
			json_args = json.dumps(obj.lazy_args, skipkeys = True, ensure_ascii = False)
		except Exception as e:
			print(9999999999, obj.lazy_args, obj.__type__)
			raise e
			
		obj.attributes['data-args'] = json_args
		return super().theme_attributes(obj, format, view_mode, args)

