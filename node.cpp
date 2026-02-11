void noofnodechild(binarytree<int>* root){
    if (root -> nullptr == 0){
        return 0;
    }
    if (root -> left == nullptr && root ->right == nullptr){
        return 1;

    }
    return noofnodechild(root->left) + noofnodechild(root->right);
}


vector <int> ans;
inordernotation(root->left);
ans.pushback(root-> data);
inordernotation(root -> right);


return (root-> left )