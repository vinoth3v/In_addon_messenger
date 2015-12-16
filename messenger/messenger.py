
class Messenger:
	''''''
	
	def message_access(self, from_nabar_id, to_nabar_id):
		# TODO: message_access
		return IN.relater.hasActiveRelationBetween('friend', 'Nabar', from_nabar_id, 'Nabar', to_nabar_id)
	
	def get_su_room_between(self, from_nabar_id, to_nabar_id):
		''''''
		try:
			
			cursor = IN.db.select({
				'table' : ['message.room', 'r'],
				'columns' : ['r.id'],
				'where' : [
					['r.type', 'su'],
					['r.status', '>=', 1],
				],
				'join' : [
					['inner join', 'message.room_nabar', 'r1', [
						['r.id = r1.room_id'],
						['r1.nabar_id', from_nabar_id],
					]],
					['inner join', 'message.room_nabar', 'r2', [
						['r.id = r2.room_id'],
						['r2.nabar_id', to_nabar_id],
					]]
				]
			}).execute()
			
			if cursor.rowcount == 0:
				return
			
			room_id = cursor.fetchone()['id']
			
			if room_id:
				return IN.entitier.load_single('Room', room_id)
			
			
		except Exception as e:
			IN.logger.debug()
		

	def create_su_room(self, from_nabar_id, to_nabar_id):
		''''''
		# TODO: access check
		
		room = Entity.new('Room', {
			'type' : 'su',
			'nabar_id' : from_nabar_id,
			'status' :  1,
		})
	
		room.save()
		
		# insert from_nabar_id
		IN.db.insert({
			'table' : 'message.room_nabar',
			'columns' : ['room_id', 'nabar_id', 'status'],
		}).execute([[room.id, from_nabar_id, 1]])
		
		# insert to_nabar_id
		IN.db.insert({
			'table' : 'message.room_nabar',
			'columns' : ['room_id', 'nabar_id', 'status'],
		}).execute([[room.id, to_nabar_id, 1]])
		
		# commit the changes
		IN.db.connection.commit()
		
		return room
	
	def send_text_message_to_room(self, message_text, room, nabar):
		# TODO: ACCESS CHECK
		
		try:
			
			message_text = message_text.strip()
			
			if not message_text:
				return
			
			# create message
			
			message = Entity.new('Message', {
				'type' : 'chat',
				'nabar_id' : nabar.id,
				'status' :  1,
				'room_id' : room.id,
			})
			
			message['field_message'].value = {
				'' : {
					0 : {
						'value' :  message_text
					}
				}
			}
			
			message.save()
			
			# create message nabar views
			if room.members:
				# insert only if any members # public room may not have members
				values = []
				for nabar_id in room.members:
					values.append([nabar_id, message.id, 1])
					
				IN.db.insert({
					'table' : 'message.message_nabar',
					'columns' : ['nabar_id', 'message_id', 'status'],
				}).execute(values)
			
			# commit the changes
			IN.db.connection.commit()
			
			return message
			
		except Exception as e:
			IN.logger.debug()
			
	def get_message_read_status(self, ids, nabar_id):
		
		status = {}
		try:
			cursor = IN.db.select({
				'table' : ['message.message_nabar', 'mn'],
				'columns' : ['mn.message_id', 'mn.status'],
				'where' : [
					['mn.nabar_id', nabar_id],
					['mn.message_id', 'IN', ids]
				]
			}).execute()
			
			if cursor.rowcount == 0:
				return status
				
			for row in cursor:
				status[row['message_id']] = row['status']
			
		except Exception as e:
			IN.logger.debug()
		
		return status
		
@IN.hook
def In_app_init(app):
	# set the messenger

	IN.messenger = Messenger()


