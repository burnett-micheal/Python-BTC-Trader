import plotly.graph_objects as go

class Chart:
  data = {}
  def addData(self, title, x, y, mode=None):
    if(title in self.data):
      self.data[title]['x'].append(x)
      self.data[title]['y'].append(y)
      self.data[title]['mode'] = mode
    else:
      self.data[title] = {'x':[x], 'y':[y], 'mode':mode}
  
  def show(self):
    plotArr = []
    for title in self.data:
      if(self.data[title]['mode'] is None):
        plotArr.append(go.Scatter(x=self.data[title]['x'], y=self.data[title]['y'], name=title))
      else:
        plotArr.append(go.Scatter(x=self.data[title]['x'], y=self.data[title]['y'], name=title, mode=self.data[title]['mode']))
    fig = go.Figure(data=plotArr)

    fig.show()