import numpy as np
import matplotlib.pyplot as plt

def sigmoid_function(x):
    return 1.0 / (1.0 + np.exp(-x))

class RegularizedLogisticRegression(object):
    '''
    Implement regularized logistic regression for binary classification.

    The weight vector w should be learned by minimizing the regularized loss
    \l(h, (x,y)) = log(1 + exp(-y <w, x>)) + \lambda \|w\|_2^2. In other words, the objective
    function that we are trying to minimize is the log loss for binary logistic regression 
    plus Tikhonov regularization with a coefficient of \lambda.
    '''
    def __init__(self):
        self.learningRate = 0.00001 # Feel free to play around with this if you'd like, though this value will do
        # self.num_epochs = 10000 # Feel free to play around with this if you'd like, though this value will do
        self.num_epochs = 10000
        self.batch_size = 15 # Feel free to play around with this if you'd like, though this value will do
        self.weights = None

        #####################################################################
        #                                                                    #
        #    MAKE SURE TO SET THIS TO THE OPTIMAL LAMBDA BEFORE SUBMITTING    #
        #                                                                    #
        #####################################################################

        self.lmbda =  1 # tune this parameter (0.83 w 1)


    def train(self, X, Y):
        '''
        Train the model, using batch stochastic gradient descent
        @params:
            X: a 2D Numpy array where each row contains an example, padded by 1 column for the bias
            Y: a 1D Numpy array containing the corresponding labels for each example
        @return:
            None
        '''
        self.weights = np.zeros(len(X[0]))
        for i in range(0,self.num_epochs):
            # shuffle examples AND labels -> so the labels are the same (both the same way)
            shuffler = np.random.permutation(len(X))
            X_shuffled = X[shuffler]
            Y_shuffled = Y[shuffler]
            for i in range(0, len(X), self.batch_size):
                xBatch = X_shuffled[i: i + self.batch_size]
                yBatch = Y_shuffled[i: i + self.batch_size]
                L = np.zeros_like(self.weights)
                # for x,y in zip(xBatch, yBatch):
                #     # for j in range(0, X.shape[1]):  
                #     #     if (y == j):
                #     #         L += (sigmoid_function(np.matmul(self.weights,x))[j] - 1) * x
                #     #     else:
                #     #         L += (sigmoid_function(np.matmul(self.weights,x))[j]) * x
                #     prob = np.matmul(self.weights,x)
                #     L += np.matmul(sigmoid_function(prob) - y, x)
                # print(xBatch.shape)
                # print(self.weights.shape)
                prob = np.matmul(xBatch, self.weights)
                L = np.matmul(sigmoid_function(prob) - yBatch, xBatch)
                self.weights -= self.learningRate * (L / len(xBatch) + (2*self.lmbda*self.weights))
            # add constant (tikhonov)
            # losses.append(self.loss(X_shuffled, Y_shuffled))
            # if (len(losses)>1 and abs(losses[-1]-losses[-2]) <= self.conv_threshold):
            #     converge = True

    def predict(self, X):
        '''
        Compute predictions based on the learned parameters and examples X
        @params:
            X: a 2D Numpy array where each row contains an example, padded by 1 column for the bias
        @return:
            A 1D Numpy array with one element for each row in X containing the predicted class.
        '''
        logits = np.matmul(self.weights, np.transpose(X))
        probabilities = np.apply_along_axis(sigmoid_function, 0, logits) #applies sigmoid to every row of logits
        predictions = np.where(probabilities > 0.5, 1, 0) #loops through probabilities
        return predictions #return index, ie, which class

    def accuracy(self,X, Y):
        '''
        Output the accuracy of the trained model on a given testing dataset X and labels Y.
        @params:
            X: a 2D Numpy array where each row contains an example, padded by 1 column for the bias
            Y: a 1D Numpy array containing the corresponding labels for each example
        @return:
            a float number indicating accuracy (between 0 and 1)
        '''
        predictions = self.predict(X)
        return np.mean(predictions == Y) #ratio of number of correct matches

    def runTrainTestValSplit(self, lambda_list, X_train, Y_train, X_val, Y_val):
        '''
        Given the training and validation data, fit the model with training data and test it with
        respect to each lambda. Record the training error and validation error, which are equivalent 
        to (1 - accuracy).

        @params:
            lambda_list: a list of lambdas
            X_train: a 2D Numpy array for trainig where each row contains an example,
            padded by 1 column for the bias
            Y_train: a 1D Numpy array for training containing the corresponding labels for each example
            X_val: a 2D Numpy array for validation where each row contains an example,
            padded by 1 column for the bias
            Y_val: a 1D Numpy array for validation containing the corresponding labels for each example
        @returns:
            train_errors: a list of training errors with respect to the lambda_list
            val_errors: a list of validation errors with respect to the lambda_list
        '''
        train_errors = []
        val_errors = []
        # loop through lambda_list
        for lambda_i in lambda_list:
            self.lmbda = lambda_i
            self.train(X_train,Y_train) #weights updated
            train_errors.append(1-self.accuracy(X_train,Y_train))
            val_errors.append(1-self.accuracy(X_val,Y_val))
        return train_errors, val_errors

    def _kFoldSplitIndices(self, dataset, k):
        '''
        Helper function for k-fold cross validation. Evenly split the indices of a
        dataset into k groups.

        For example, indices = [0, 1, 2, 3] with k = 2 may have an output
        indices_split = [[1, 3], [2, 0]].
        
        Please don't change this.
        @params:
            dataset: a Numpy array where each row contains an example
            k: an integer, which is the number of folds
        @return:
            indices_split: a list containing k groups of indices
        '''
        num_data = dataset.shape[0]
        fold_size = int(num_data / k)
        indices = np.arange(num_data)
        np.random.shuffle(indices)
        indices_split = np.split(indices[:fold_size*k], k)
        return indices_split

    def runKFold(self, lambda_list, X, Y, k = 3):
        '''
        Run k-fold cross validation on X and Y with respect to each lambda. Return all k-fold
        errors.
        
        Each run of k-fold involves k iterations. For an arbitrary iteration i, the i-th fold is
        used as testing data while the rest k-1 folds are combined as one set of training data. The k results are
        averaged as the cross validation error.

        @params:
            lambda_list: a list of lambdas
            X: a 2D Numpy array where each row contains an example, padded by 1 column for the bias
            Y: a 1D Numpy array containing the corresponding labels for each example
            k: an integer, which is the number of folds, k is 3 by default
        @return:
            k_fold_errors: a list of k-fold errors with respect to the lambda_list
        '''
        k_fold_errors = []
        indices = []
        for lmbda in lambda_list:
            self.lmbda = lmbda
            #[TODO] call _kFoldSplitIndices to split indices into k groups randomly
            new_indices = self._kFoldSplitIndices(X, k)
            #[TODO] for each iteration i = 1...k, train the model using lmbda
            # on k???1 folds of data. Then test with the i-th fold.
            train_errors = []
            for i in range(0,k):
                test_set = X[new_indices[i]] #test fold
                test_labels = Y[new_indices[i]] #test labels
                # training_set = np.concatenate((indices[:i], indices[i+1:]), axis=None)
                training_set = new_indices[i:] + new_indices[:i+1]
                t_indices = np.array(training_set).flatten()
                
                
                self.train(X[t_indices], Y[t_indices])
                train_errors.append(1-(self.accuracy(test_set, test_labels)))
                #self.train(self.train(X,Y))

            #[TODO] calculate and record the cross validation error by averaging total errors
            k_fold_errors.append(np.mean(train_errors)) #averages total errors using mean

        return k_fold_errors

    def plotError(self, lambda_list, train_errors, val_errors, k_fold_errors):
        '''
        Produce a plot of the cost function on the training and validation sets, and the
        cost function of k-fold with respect to the regularization parameter lambda. Use this plot
        to determine a valid lambda.
        @params:
            lambda_list: a list of lambdas
            train_errors: a list of training errors with respect to the lambda_list
            val_errors: a list of validation errors with respect to the lambda_list
            k_fold_errors: a list of k-fold errors with respect to the lambda_list
        @return:
            None
        '''
        plt.figure()
        plt.semilogx(lambda_list, train_errors, label = 'training error')
        plt.semilogx(lambda_list, val_errors, label = 'validation error')
        plt.semilogx(lambda_list, k_fold_errors, label = 'k-fold error')
        plt.xlabel('lambda')
        plt.ylabel('error')
        plt.legend()
        plt.show()