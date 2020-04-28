# COVID-19-classifier

### Classification of COVID-19 infection in pulmonary images using Transfer learning approach

#### Abstract

The world is facing a pandemic, COVID-19 which has affected more than a million people worldwide. This is a viral infectious disease caused by a novel SARS-CoV-2 virus. The clinical picture of the disease is not very comprehensive and most lethality has been recorded due to upper respiratory tract infections. This study aims to identify and separate pneumonia infected COVID-19 lungs from other pneumonia and normal patients using pulmonary diagnostic imaging data (chest X-ray will be used). These images are accessed from databases, COVID-19 database by RISM and a Github repository, Covid Chest X-ray database. Some researchers have also released relevant datasets on Preprint servers with some other pre-existing lung X-rays and CT scans. All of these images contain COVID positive patient lung images, normal and pneumonia ones. Transfer learning approach was used to train one such dataset and classify images into  COVID-19 positive and other classes. The models used were based on the VGG framework (VGG16 and VGG19). Both of these models performed well but, the accuracy was not a very robust measure for the misclassification. The limitations of this study lie in the insufficiency of imaging data, improper orientation of images at this time and computational hindrance along with the misclassifications that exists in the very models. 