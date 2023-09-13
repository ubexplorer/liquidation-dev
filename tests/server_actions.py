if not record.date_deadline:
  raise Warning('Task has no deadline!')
delta = record.date_deadline - datetime.date.today()
days = delta.days
if days==0:
  msg = 'Task is due today.'
elif days < 0:
  msg = 'Task is %d day(s) late.' % abs(days)
else:
  msg = 'Task will be due in %d day(s).' % days
record.message_post(body=msg, subject='Reminder', message_type='notification', subtype_xmlid='mail.mt_comment')