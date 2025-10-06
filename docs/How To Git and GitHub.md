Status: #literature 
Tags: `=this.file.tags`
Links: `=this.file.outlinks`

---
See this: [https://rogerdudler.github.io/git-guide/](https://rogerdudler.github.io/git-guide/)

Git and GitHub is the main system that programmers use to collaborate and perform version control. **GitHub** stores a programming project (repository) in a cloud server that contributors can retrieve and work on independently. **Git** is a command-line tool to perform certain operations on a repository. In order to have access to a private repository or publish on a public one, users must have a GitHub account and be marked as a contributor by the project admin.

## Saving Changes

There are 3 “levels” to modifying a repo, each with increasing consequence:

1. `git add <filename>` adds a file’s modifications to an index
2. `git commit -m "message"` commits the indexed change. The message is not optional
3. `git push` pushes all committed changes to the current branch remote repo. This can be reversed by rolling back the push.

## Branches

A **branch** in a repo is like a parallel timeline that splits where something is different. Every project will have a **main branch** (usually the one that is deployed), but most will also have feature branches. Users can split off from a branch to work on a feature, without worrying about corrupting the main branch’s function. Once a user completes a feature and tests it fully, they can request to merge it back into the main branch with a **pull request**. This can be done on GitHub via the menus or can be done via Git using the commands:

1. `git checkout -b <branch_name>` creates a branch
2. `git checkout <branch_name>` switches from current branch to named one
3. `git branch -d <branch_name>` deletes branch
4. `git push origin <branch>` pushes the branch to the remote repository
# References
