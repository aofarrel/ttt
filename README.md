# ttt
Tweak Terra's Tables -- A toolkit for modifying data tables used by [terra.bio](https://terra.bio/)

Terra's data tables can be drawn upon by workflows in order to easily set up inputs. With the power of tables, you can run a workflow on thousands of files, simply telling Terra to use the contents of a column in a datatable as the input. 
| entity:file_id | location                   |
|----------------|----------------------------|
| 0001           | gs://your_bucket/0001.cram |
| 0002           | gs://your_bucket/0002.cram |
| 0003           | gs://your_bucket/0003.cram |
| 0004           | gs://your_bucket/0004.cram |
| 0005           | gs://your_bucket/0005.cram |
| 0006           | gs://your_bucket/0006.cram |
| 0007           | gs://your_bucket/0007.cram |

----->  Run workflow(s) with inputs defined by data table
        Select root entity type: **file**
----->  Task Name Variable  Type  Attribute
        TopMedAligner input_cram_file File  **this.location**


Each input of your workflow can use a column on a data table, and data tables can reference other data tables. For instance, CRAI data tables imported from Gen3 reference their parent CRAM files, which are located in another table, using a UID. 

These tables are essentially TSV files with a very specific format, so as long as we follow that format, we can generate them programmatically using iPython notebooks.

### BYOGen3
If you want to combine your own data with TOPMed data, this will do it for you, combining BYOD with Gen3.

### BYODGen3 Extended
![A surprise tool that will help us later](https://i.kym-cdn.com/photos/images/newsfeed/001/264/842/220.png)

### Bucket List
Simple method of programmatically generating a TSV from files already in a workspace's Google Bucket. The resulting table will just have two columns. It does not distinguish between files of different extensions. The more complicated file-aware version is Paternity Test.

### Drops in a Bucket
Debug notebook that generates 1000s of test files. Probably useful only to me.

### Paternity Test
Works a bit like Bucket List in concept, but will attempt to link files that are related. For instance, CRAM and CRAI files, or VCF and CSI files. Each row is anchored by one "parent" file (such as the CRAM file) and will contain its children (such as the CRAI file) on the same row in different columns. There is no theoretical maximum to the number of linkages -- a "parent" file can have dozens of "children." The user only needs to select the file extension that will be considered the parent. Although this was inspired by the Gen3 multi-table data model, the output is just a single table rather than tables linked to each other.

### Psuedofolder Maker
Extremely niche notebook for manually creating a psuedofolder in a Google Cloud bucket. Not useful to most people.
