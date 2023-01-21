# برنامه تست ۱

لطفا برداشت خودتان از متن زیر را پیاده سازی کنید و سوالی در مورد تفسیر این متن پرسیده نشود. برآورد ما این است که انجام این کار حداکثر به ۵ ساعت زمان نیاز داشته باشد.



دو پایگاه داده A و B با یک جدول با شمای یکسان. این جدول شامل دو ستون می باشد. یک ستون از نوع uuid و یک ستون ان نوع رشته

یک برنامه (به نام SNK) بنویسید که این دو جدول را به صورت realtime سینک کند یعنی رکوردهایی که در A نیست و در B هست را در A نیز ایجاد کند و بالعکس. این برنامه باید سرعت بالایی داشته باشد و اگر مثلا رکورد جدیدی در A بوجود آید در فاصله کمی متوجه شود و رکورد را در B نیز ایجاد کند.

SNK فقط باید بوسیله یک ORM به پایگاه داده متصل شود و نباید از روش های low level که در خود پایگاه داده برای replication تعبیه شده است استفاده کند.

لطفا از پستگرس به عنوان پایگاه داده استفاده کنید

توجه شود که این برنامه سینک کننده به صورت یک پروسس مجزا اجرا می‌شود و هیچ اطلاع و کنترلی روی نحوه وارد شدن داده به دو پایگاه داده مذکور  از کانال های دیگر ندارد.



به علاوه یک برنامه دیگر (به نام TST) که آن هم به صورت یک پروسس مجزا اجرا می‌شود نوشته شود:

TST برای تست  SNK استفاده می شود.

TST از یک حلقه بی نهایت تشکیل شده است

در هر تناوب به صورت تصادفی یکی از دو پایگاه داده را انتخاب می‌کند و تعداد ۱۰۰۰ رکورد به صورت بالک اینسرت و با محتوای تصادفی به جدول مذکور در  آن پایگاه داده اضافه می‌کند.

لطفا در ایتریشن ها از sleep استفاده نکنید و بگذارید این برنامه با حداکثر سرعت  ممکن رکوردهای جدید را به پایگاه داده ها وارد کند.



پس از نوشتن این دو برنامه و اجرای آنها خودتان به گونه ای از صحت عملکرد SNK مطمئن شوید

تاکید دوباره: SNK و TST نباید هیچ ارتباطی با یکدیگر داشته باشند و هر کدام فقط باید با پایگاه داده مرتبط باشند

# Assumptions

* No updates or delete actions will be happened in either of databases.
* There are no duplicate records before running SNK service.
* SNK service may be restarted , and it will not be happened in **committing phases**.
* There is an id column in each table in addition to uuid and data(str type) columns in order to limit query records.

## Configuration
In the **.env** file in root directory of project you'll see all configurations that can be changed.
```
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
FIRST_DB_HOST=first_db
SECOND_DB_HOST=second_db
DB_PORT=5432

REDIS_HOST=snk_redis
REDIS_PORT=6379

```

## Running
In order to run project simply setup *.env* file and run following command inside root of project.

    //Linux
    [project_root_directory] :$ docker-compose up -d --build

## Description
Synchronization steps are as follows:

1. At first no records is synced.
2. At first there is a persistent cache that has no records in it. These records define previous synced records and will be updated in step 11.
3. We will query both databases and list 200 records from each one.
4. We will save last record id that is going to be synced from each database.
5. We have a set of tuples that contain uuid and data column.
6. We will check if any of these set items had been synced before by checking if that record does exist in cache.
7. We will filter step 3 queried records in step 6, and now we have not duplicate records.
8. We will bulk insert not duplicate records in each db accordingly.
9. We will set inserted records to cache so that if the next time those record were going to be inserted in the same original database, they will be filtered in step 6.
10. If a duplicate record was going to be added in original database and filtered out once we have to delete that key from cache, in order to prevent high memory usage over time.
11. At last records will be committed to their databases accordingly and the last synced record id will be saved in cache for filter query result of step 3.
12. Goto step 3.

# Results
With current codes synchronization process (SNK) was getting behind bulk insertion process (TST) in speed.
According to tests after inserting 1000K records only 440K records were synced between two databases.

Another scenario without using redis implemented that was using python parameters as cache and in this scenario we 
could almost handle this amount of bulk insertion by TST.\
According to tests after inserting 1000K records 920K records were synced between two databases. The downside of this scenario is that if SNK process synchronized some records, and then process restarted, It will try to add duplicate keys to databases.

This SNK service is not fault-tolerant because there is a need to implement transaction mechanism for cache too

# Accomplishments
In this project I have tried to code in a way that, in case of needing to change any part like cache, repository, orm, etc, 
there will be no need to change other logical parts
