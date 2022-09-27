class UniqueId:
  _id = 1
  def get(self):
    idCopy = self._id
    self._id += 1
    return idCopy