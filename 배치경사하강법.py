import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

cancer = load_breast_cancer()
x = cancer.data
y = cancer.target
x_train_all, x_test, y_train_all, y_test = train_test_split(x, y, stratify=y, test_size=0.2, random_state=42)
x_train, x_val, y_train, y_val = train_test_split(x_train_all, y_train_all, stratify=y_train_all, test_size=0.2, random_state=42)

print(x_train.shape, x_val.shape) #훈련 전 데이터의 크기를 확인하는 습관을 가지자.

class SingleLayer:

  def __init__(self, learning_rate=0.1, l1=0, l2=0):
    self.w = None
    self.b = None
    self.losses = []
    self.val_losses = []
    self.w_history = []
    self.lr = learning_rate
    self.l1 = l1
    self.l2 = l2

  def forpass(self, x):
    z=np.dot(x,self.w) + self.b #np.sum말고 np.dot으로 행렬의 곱셈을 함.
    return z

  def backprop(self, x, err):
    m = len(x)
    w_grad = np.dot(x.T, err)/m #x.T는 x행렬을 전치시킨 것(행과 열을 뒤바꿈)으로 err과 곱하고 x 갯수로 나누어 w행렬에 곱할 수 있는 모양으로 만듦.
    b_grad = np.sum(err)/m
    return w_grad, b_grad

  def activation(self, z):
    a = 1/(1+np.exp(-z))
    return a

#배치경사하강법에서는 전체 샘플을 한꺼번에 계산하므로 for문이 사라짐
  def fit(self, x, y, epochs=100, x_val=None, y_val=None):
    y = y.reshape(-1, 1) #타깃을 열벡터로 바꿈
    y_val = y_val.reshape(-1, 1)
    m = len(x)
    self.w = np.ones((x.shape[1], 1)) #가중치 초기화
    self.b = 0
    self.w_history.append(self.w.copy()) #가중치 기록

    for i in range(epochs):
      z = self.forpass(x)
      a = self.activation(z)
      err = -(y-a)
      w_grad, b_grad = self.backprop(x,err)
      w_grad += (self.l1*np.sign(self.w) + self.l2*self.w) / m
      self.w -= self.lr * w_grad
      self.b -= self.lr*b_grad
      self.w_history.append(self.w.copy())
      a = np.clip(a, 1e-10, 1-1e-10)
      loss = np.sum(-(y*np.log(a) + (1-y)*np.log(1-a)))
      self.losses.append((loss + self.reg_loss()) / m)
      self.update_val_loss(x_val, y_val)

  def predict(self, x):
    z = self.forpass(x)
    return z>0

  def score(self, x, y):
    return np.mean(self.predict(x) == y.reshape(-1, 1))

  def reg_loss(self):
    return self.l1*np.sum(np.abs(self.w)) + self.l2/2*np.sum(self.w**2)

  def update_val_loss(self, x_val, y_val):
    z = self.forpass(x_val)
    a = self.activation(z)
    a = np.clip(a, 1e-10, 1-1e-10)
    val_loss = np.sum(-(y_val*np.log(a) + (1-y_val)*np.log(1-a)))
    self.val_losses.append((val_loss + self.reg_loss()) / len(y_val))

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(x_train) #fit을 이용해 변환규칙을 익힘
x_train_scaled = scaler.transform(x_train)
x_val_scaled = scaler.transform(x_val)

single_layer = SingleLayer(l2=0.01)
single_layer.fit(x_train_scaled, y_train, x_val=x_val_scaled, y_val=y_val, epochs=10000) #배치경사하강법은 한번만에 전부 계산하기 때문에 에포크를 늘릴 필요가 있음.
single_layer.score(x_val_scaled, y_val)

plt.ylim(0, 0.3) #y가 0 ~ 0.3으로 나타남
plt.plot(single_layer.losses)
plt.plot(single_layer.val_losses)
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train_loss', 'val_loss'])
plt.show()
