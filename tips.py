
def tips(respond):
    num1=respond['num1']
    num2=respond['num2']
    answer=respond['answer']
    result = num1*num2
    if num1==1 or num2==1:
        tip = 'When you multiply a number with 1 The number is staying the same'
    elif num1==2 or num2==2:
        if num1==2:
            k=num2
        elif num2==2:
            k=num1
        tip = 'The trick is to calculate {} plus {}'.format(k,k)
    elif num1==9 or num2==9:
        if num1==9:
            k=num2
        elif num2==9:
            k=num1
        tip = 'The trick is to calculate 10 multiple {}, and then subtract 9'.format(k)
    elif num1==10 or num2==10:
        tip = 'When you see 10, just add 0 to the other number'
    elif (num1==5 or num2==5) and result%5!=0:
        tip = 'multiplication with 5, the result is always end with 5 or 0'
    elif abs(result-answer)<=2:
        tip = 'So close. I am sure next time we will know the answer'
    elif (num1==7 or num2==7) and (num1!=5 or num2!=5):
        tip = 'it is hard calculation. you know 7 multiple 5, so try to continue from this point'
    elif (num1==6 or num2==6) and (num1!=5 or num2!=5):
        tip = 'it is hard calculation. you know 6 multiple 5, so try to continue from this point'
    elif (num1==8 or num2==8) and (num1!=5 or num2!=5):
        tip = 'it is hard calculation. you know 6 multiple 5, so try to continue from this point'
    return tip


# In[7]:


tips({'num1':10,'num2':3, 'answer':29})

