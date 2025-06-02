#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/timer.h>
#include <linux/mutex.h>

#define DEVICE_NAME "foobar_sdec"
#define CLASS_NAME "tp5"
#define TRIANGULAR_STEP 2
#define SQUARE_PERIOD_MS 500
#define TRIANGULAR_PERIOD_MS 10
#define SAWTOOTH_PERIOD_MS 50
#define SAWTOOTH_STEP 2

static dev_t dev_num;
static struct cdev cdev;
static struct class *foobar_class;

static struct timer_list signal_timer;
static DEFINE_MUTEX(signal_mutex);

static unsigned long last_square_jiffies = 0;
enum signal_type { SQUARE = 1, TRIANGULAR = 2, SAWTOOTH = 3 }; // Add SAWTOOTH
static int sawtooth_value = 0;


static int active_signal = SQUARE;
static int square_state = 0;
static int triangular_value = 0;
static int triangular_dir = 1; // 1 = up, -1 = down

static void update_signals(struct timer_list *t) {
    mutex_lock(&signal_mutex);

    // Update square signal
    if (time_after(jiffies, last_square_jiffies + msecs_to_jiffies(SQUARE_PERIOD_MS))) {
        square_state = !square_state;
        last_square_jiffies = jiffies;
    }

    // Update triangular signal
    triangular_value += triangular_dir * TRIANGULAR_STEP;
    if (triangular_value >= 100 || triangular_value <= 0)
        triangular_dir *= -1;

    // Update sawtooth signal
    sawtooth_value += SAWTOOTH_STEP;
    if (sawtooth_value >= 100)
        sawtooth_value = 0;

    mutex_unlock(&signal_mutex);

    mod_timer(&signal_timer, jiffies + msecs_to_jiffies(TRIANGULAR_PERIOD_MS));
}

// File operations

static ssize_t foobar_read(struct file *file, char __user *buf, size_t len, loff_t *offset) {
    int value;
    char out[16];
    int out_len;

    mutex_lock(&signal_mutex);
    if (active_signal == SQUARE)
        value = square_state;
    else if (active_signal == TRIANGULAR)
        value = triangular_value;
    else if (active_signal == SAWTOOTH) // Add sawtooth signal handling
        value = sawtooth_value;
    mutex_unlock(&signal_mutex);

    out_len = snprintf(out, sizeof(out), "%d\n", value);
    if (*offset > 0) return 0; // EOF
    if (copy_to_user(buf, out, out_len)) return -EFAULT;

    *offset += out_len;
    return out_len;
}

static ssize_t foobar_write(struct file *file, const char __user *buf, size_t len, loff_t *offset) {
    char input;
    if (copy_from_user(&input, buf, 1)) return -EFAULT;

    mutex_lock(&signal_mutex);
    if (input == '1') 
        active_signal = SQUARE;
    else if (input == '2') 
        active_signal = TRIANGULAR;
    else if (input == '3') // Add handling for sawtooth signal
        active_signal = SAWTOOTH;
    mutex_unlock(&signal_mutex);

    return len;
}

static int foobar_open(struct inode *inode, struct file *file) {
	return 0;
}

static int foobar_release(struct inode *inode, struct file *file) {
	return 0;
}

static const struct file_operations fops = {
	.owner = THIS_MODULE,
	.open = foobar_open,
	.release = foobar_release,
	.read = foobar_read,
	.write = foobar_write,
};

static int __init foobar_init(void) {
	if (alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME) < 0)
		return -1;

	cdev_init(&cdev, &fops);
	if (cdev_add(&cdev, dev_num, 1) < 0)
		return -1;

	foobar_class = class_create(CLASS_NAME);
	if (IS_ERR(foobar_class)) return PTR_ERR(foobar_class);

	device_create(foobar_class, NULL, dev_num, NULL, DEVICE_NAME);

	timer_setup(&signal_timer, update_signals, 0);
	mod_timer(&signal_timer, jiffies + msecs_to_jiffies(TRIANGULAR_PERIOD_MS));

	pr_info("foobar_sdec: driver loaded\n");
	return 0;
}

static void __exit foobar_exit(void) {
	del_timer_sync(&signal_timer);
	device_destroy(foobar_class, dev_num);
	class_destroy(foobar_class);
	cdev_del(&cdev);
	unregister_chrdev_region(dev_num, 1);
	pr_info("foobar_sdec: driver unloaded\n");
}

module_init(foobar_init);
module_exit(foobar_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Foobar SdeC");
MODULE_DESCRIPTION("Foobar - Character Device Driver");
