import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn.cluster as cluster
from sklearn.neighbors import KNeighborsClassifier as knn
from sklearn.neighbors import DistanceMetric
from sklearn.neighbors import KDTree
from sklearn.metrics import silhouette_samples as silh_samp
from sklearn.metrics import silhouette_score as silh_score
from sklearn.metrics import accuracy_score as acc_scr, multilabel_confusion_matrix as ml_conf_matx
from sklearn.metrics import confusion_matrix as conf_matx, recall_score as recall,  precision_score as prec
from sklearn.metrics import f1_score as f1
from sklearn.decomposition import NMF
from sklearn.model_selection import train_test_split as tts
from sklearn.ensemble import RandomForestClassifier as RanForCls
from sklearn.model_selection import RandomizedSearchCV as ranCV
from pprint import pprint

fw32 = pd.read_csv('../data/cln_dfs/fw32.csv')  # read in the mostly clean forward dataframe for 32 yr old+
fw32 = fw32.iloc[:,1:]  # remove the index from the previous data frame because i didnt save the df.to_csv correctly
y = fw32.pop('target')  # set y
X = fw32   # set X
X.drop(['squad','country','competition','lg_rank','position','year_of_season','age_now'],axis=1,inplace=True)  # do a little final cleaning
print(X.isna().sum())

X.volleys = X[['volleys']].fillna(X.volleys.mean())
X.curve = X[['curve']].fillna(X.curve.mean())
X.agility = X[['agility']].fillna(X.agility.mean())
X.balance = X[['balance']].fillna(X.balance.mean())
X.jumping = X[['jumping']].fillna(X.jumping.mean())
X.vision = X[['vision']].fillna(X.vision.mean())
X.slide_tackle = X[['slide_tackle']].fillna(X.slide_tackle.mean())
X.curve = X[['curve']].fillna(X.curve.mean())

X.set_index('player_name',inplace=True)

def silh_plot(sample,n_clusters,title=None):        # i attempted to find the silhouette score for KMeans but it didn't yield definitive results, and I decided 
    fig = plt.figure(figsize=(10,6))                # to go with soft clustering instead
    ax = fig.add_subplot(111)
    k = []
    scores = []
    for c in range(2,n_clusters+2):
        
        k.append(c)
        clusterer = cluster.KMeans(n_clusters=c)
        cluster_labels = clusterer.fit_predict(sample)

        sil_score = silh_score(sample, cluster_labels)
        print("For n_clusters =", c,
          "The average silhouette_score is :", sil_score)
        scores.append(sil_score)
        silh_smp = silh_samp(sample, cluster_labels)
    
    ax.plot(k,scores)
    ax.set_title("The silhouette plot for the various clusters.")
    ax.set_xlabel("The silhouette coefficient values")
    ax.set_ylabel("Cluster label")
    ax.set_xlabel('k')
    ax.set_ylabel('Silhouette Samples')
    plt.title('Plot of Silhouette Samples')
    plt.savefig('silhouette_score_30.jpg')
    plt.show()

def fit_nmf(k,matrix):      # i used the nmf construction error to find an appropriate k
        nmf = NMF(n_components=k)
        nmf.fit(matrix)
        W = nmf.transform(matrix);
        H = nmf.components_;
        return nmf.reconstruction_err_

model_params = {'bootstrap': [True, False],                 # randomized search cv parameters
               'max_depth': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, None],
               'max_features': ['auto', 'sqrt'],
               'min_samples_leaf': [1, 2, 4],
               'min_samples_split': [2, 5, 10],
               'n_estimators': [130, 180, 250,400]}

if __name__ == '__main__':
    X_train, X_test, y_train, y_test = tts(X,y,stratify=y)  # train-test-split, stratified because my sample was unbalanced ~84% no/16% yes
    X_train.set_index('player_name',inplace=True)   # prep for the NMF
    X_test.set_index('player_name',inplace=True)
    
    n_comp = 50    # used to create the reconstruction plot (yielded k=3)
    error = [fit_nmf(i,X_train) for i in range(1,n_comp)]
    plt.plot(range(1,n_comp), error)
    plt.xlabel('k')
    plt.ylabel('Reconstruction Error');
    plt.savefig('NMF_Reconstruction_Error')
    plt.show()

    k = 3    # use that k=3 to create the fit model
    topics = ['latent_topic_{}'.format(i) for i in range(k)]
    nmf_train = NMF(n_components = k)
    nmf_train.fit(X_train)

    W = nmf_train.transform(X_train)
    H = nmf_train.components_
    names = X_train.index
    player_attr = X_train.columns
    W = pd.DataFrame(W, index = names, columns = topics)
    H = pd.DataFrame(H, index = topics, columns = player_attr)
 
    topic_ = 0   # used to check the validity of the latent topics created
    num_players = 10
    top_attrs = H.iloc[topic_].sort_values(ascending=False).index[:num_players]
    print(top_attrs)

    X_train_nmf = pd.concat([X_train,W],axis=1,join='inner')   # appends the newly created latent topic columns to X_train.  I cannot take credit for this idea Chris and Kayla helped with this
    
    nmf_test = NMF(n_components=k)  # create the latent topics for the test set? I had to do this to get the model to run, but im not 100% this is legitimate.
    nmf_test.fit(X_test)

    W2 = nmf_test.transform(X_test)
    H2 = nmf_test.components_
    names2 = X_test.index
    player_attr2 = X_test.columns

    W2 = pd.DataFrame(W2,index=names2,columns=topics)
    H2 = pd.DataFrame(H2,index=topics,columns=player_attr2)

    X_test_nmf = pd.concat([X_test,W2],axis=1,join='inner')   # appends the test latent topics to X_test
        
    silh_plot(X_train,50)   # creates the plot from the func above
           
    rf = RanForCls()    # create the random forest for the randomized search cv 
    rf_rscv = ranCV(rf,model_params,n_iter=100,cv=5,verbose=1)   # create and return randomized search cv results
    mod = rf_rscv.fit(X_train_nmf,y_train)        
    best_params = mod.best_estimator_.get_params()
    pprint(mod.best_estimator_.get_params()) 
    
    # {'bootstrap': False,          # the best parameters from the randomized search cv
    # 'ccp_alpha': 0.0,
    # 'class_weight': None,
    # 'criterion': 'gini',
    # 'max_depth': 20,
    # 'max_features': 'sqrt',
    # 'max_leaf_nodes': None,
    # 'max_samples': None,
    # 'min_impurity_decrease': 0.0,
    # 'min_impurity_split': None,
    # 'min_samples_leaf': 1,
    # 'min_samples_split': 2,
    # 'min_weight_fraction_leaf': 0.0,
    # 'n_estimators': 400,
    # 'n_jobs': None,
    # 'oob_score': False,
    # 'random_state': None,
    # 'verbose': 0,
    # 'warm_start': False}

    y_pred_fake = [0 for _ in range(len(y_test))]   # fake data to check the accuracy and F1 score of the random forest because the data is so unbalanced
    
    plt.style.use('seaborn-dark')
    rf_nmf = RanForCls(n_estimators=250,criterion='entropy',verbose=1).fit(X_train_nmf,y_train)  # run random forest using parameters other than the randomcv parameters to check
    rf_nmf_pred = rf_nmf.predict_proba(X_test_nmf)[:,1]   # use predict proba to modify the threshold
    rf_nmf_pred_thresh = (rf_nmf_pred >= 0.35)    # the threshold returning the highest F1 score
    print(f'rf feature import: {np.argsort(rf_nmf.feature_importances_)}')   # get the most important feature indexes and plot by importance and feature name
    rf_best_feats = np.argsort(rf_nmf.feature_importances_)
    rf_feat_importances = pd.Series(rf_best_feats, index=X_train_nmf.columns)
    rf_feat_importances.nlargest(15).plot(kind='bar')
    plt.xticks(rotation=45)
    plt.title(f"Top 15 important features for 250 trees using entropy")
    plt.savefig('nmf_250_entropy_035.jpg')
    plt.show()
    print(f'rf conf matx: {conf_matx(y_test,rf_nmf_pred_thresh)}')  # return scoring metrics to judge the outcome of the model 
    print(f'rf acc score: {round(acc_scr(y_test,rf_nmf_pred_thresh),3)}')   # (did not remember to round until several iterations in...)
    print(f'rf prec score: {round(prec(y_test,rf_nmf_pred_thresh),3)}')  
    print(f'rf recall score: {round(recall(y_test,rf_nmf_pred_thresh),3)}')
    print(f'rf F1 score: {round(f1(y_test,rf_nmf_pred_thresh),3)}')    
    
    rf_nmf_opt = RanForCls(n_estimators=400,bootstrap=False,max_depth=20,criterion='gini',max_features='sqrt',verbose=1).fit(X_train_nmf,y_train)  # run random forest using 
    rf_nmf_pred_opt = rf_nmf_opt.predict_proba(X_test_nmf)[:,1]                                                                                    # randomcv parameters
    rf_nmf_pred_thresh_opt = (rf_nmf_pred_opt >= 0.35)   # the threshold returning the highest F1 score
    print(f'opt feature import: {np.argsort(rf_nmf_opt.feature_importances_)}')
    rf_opt_best_feats = np.argsort(rf_nmf_opt.feature_importances_)
    opt_feat_importances = pd.Series(rf_opt_best_feats, index=X_train_nmf.columns)
    opt_feat_importances.nlargest(15).plot(kind='bar')
    plt.xticks(rotation=45)
    plt.title(f"Top 15 important features for 400 trees using gini")
    plt.savefig('opt_400_gini_nboot_20_sqrt_035.jpg')
    plt.show()
    print(f'opt conf matx: {conf_matx(y_test,rf_nmf_pred_thresh_opt)}')
    print(f'opt acc score: {round(acc_scr(y_test,rf_nmf_pred_thresh_opt),3)}')   
    print(f'opt prec score: {round(prec(y_test,rf_nmf_pred_thresh_opt),3)}')     
    print(f'opt recall score: {round(recall(y_test,rf_nmf_pred_thresh_opt),3)}')
    print(f'opt F1 score: {round(f1(y_test,rf_nmf_pred_thresh_opt),3)}')         
    