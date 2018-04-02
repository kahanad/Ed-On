
import pandas as pd
import numpy as np
import os


class Model:
    def __init__(self, user_id):
        self.id = user_id
        self.questions = self.start()
        self.P_S = 0.15
        self.P_G = 0.01
        self.text_questions = self.text_Q()

    def text_Q(self):
        my_file = './user_data/questions_list.csv'
        df = pd.read_csv(my_file, delimiter=',', header=None)
        return df[0].values.tolist()

    def initial_matrix(self):
        questions= np.zeros((10,10),dtype=float)
        questions[0,:]=0.9
        questions[:,0]=0.9
        questions[1,1:5]=0.8
        questions[1,5:9]=0.75
        questions[2,2:5]=0.7
        questions[2,5:9]=0.65
        questions[3,3:5]=0.6
        questions[3,5:9]=0.5
        questions[4,4:9]=0.5
        questions[5,5:9]=0.3
        questions[6,6:9]=0.3
        questions[7,7:9]=0.3
        questions[8,8]=0.3
        questions[1:,9]=0.8
        for i in range(10):
            for j in range(10):
                questions[j,i]=questions[i,j]
        return questions


    def update_R(self,i,j,result):
        P_T = np.average(self.questions)
        if result==1:
            P_temp = (self.questions[i,j]*(1-self.P_S))/(self.questions[i,j]*(1-self.P_S)+(1-self.questions[i,j])*self.P_G)
        if result==0:
            P_temp = (self.questions[i,j]*(self.P_S))/(self.questions[i,j]*(self.P_S)+(1-self.questions[i,j])*(1-self.P_G))
        self.questions[i,j] = min(P_temp+(1-P_temp)*P_T,0.95)
        self.questions[j,i] = min(P_temp+(1-P_temp)*P_T,0.95)
        return self.questions


    def d_calculate(self,row,col,row_tag, col_tag, result):
        if result==1:
            d = abs(row_tag-row)+abs(col_tag-col)
            if d==1:
                return min(self.questions[row_tag,col_tag]*1.1,0.95)
            if d==2:
                return min(self.questions[row_tag,col_tag]*1.05,0.95)
            else:
                return self.questions[row_tag,col_tag]
        else:
            d = abs(row_tag-row)+abs(col_tag-col)
            if d==1:
                return max(self.questions[row_tag,col_tag]*0.9,0.05)
            if d==2:
                return max(self.questions[row_tag,col_tag]*0.95,0.05)
            else:
                return self.questions[row_tag,col_tag]


    def update_by_D(self,i,j,result):
        if result==1:
            for row in range(10):
                for col in range(10):
                    d = abs(i-row)+abs(j-col)
                    if d==1:
                        self.questions[row,col] = min(self.questions[row,col]*1.1,0.95)
                    if d==2:
                        self.questions[row,col] = min(self.questions[row,col]*1.05,0.95)
        else:
            for row in range(10):
                for col in range(10):
                    d = abs(i-row)+abs(j-col)
                    if d==1:
                        self.questions[row,col] = max(self.questions[row,col]*0.9,0.05)
                    if d==2:
                        self.questions[row,col] = max(self.questions[row,col]*0.95,0.05)
        return self.questions


    def select_question(self):
        questions_I = np.zeros((10,10),dtype=float)
        for row in range(10):
            for col in range(10):
                counter = 0
                for row_tag in range(10):
                    for col_tag in range(10):
                        p_c = self.d_calculate(row,col,row_tag, col_tag, 1)
                        p_w = self.d_calculate(row,col,row_tag, col_tag, 0)
                        q = self.questions[row_tag,col_tag]
                        counter+= q*(-p_c*np.log(q/p_c))+(1-q)*(-p_w*np.log(q/p_w))
                questions_I[row,col] = counter
        return np.unravel_index(questions_I.argmax(), questions_I.shape)



    def select_text(self,i,j):
        k = np.random.randint(0,len(self.text_questions))
        text = self.text_questions[k].format(i+1,j+1)
        return text


    def start(self):
        my_file = str(self.id) + '.csv'
        if my_file in os.listdir('./user_data'):
            new_matrix = np.genfromtxt('./user_data/'+my_file, delimiter=',')
            return new_matrix
        else:
            return self.initial_matrix()


    def save_file(self):
        np.savetxt('./user_data/'+str(self.id)+'.csv', self.questions, delimiter= ',')


    def flow_1(self):
        R = self.select_question()
        text = self.select_text(R[0],R[1])
        result = (R[0]+1)*(R[1]+1)
        return {'string': text, 'num1': R[0]+1, 'num2':R[1]+1, 'result': result}


    def flow_2(self,respond):
        result = (respond['num1'])*(respond['num2'])
        if respond['answer'] == result:
            self.questions = self.update_R(respond['num1']-1,respond['num2']-1,1)
            self.questions = self.update_by_D(respond['num1']-1,respond['num2']-1,1)
            self.questions = self.update_by_D(respond['num2']-1,respond['num1']-1,1)
        else:
            self.questions = self.update_R(respond['num1']-1,respond['num2']-1,0)
            self.questions = self.update_by_D(respond['num1']-1,respond['num2']-1,0)
            self.questions = self.update_by_D(respond['num2']-1,respond['num1']-1,0)

        R = self.select_question()
        text = self.select_text(R[0],R[1])
        result = (R[0]+1)*(R[1]+1)
        return {'string': text, 'num1': R[0]+1, 'num2':R[1]+1, 'result': result}