#!/usr/bin/env python3

from datetime import datetime, timedelta
import os
import difflib
import random, string
import re
import subprocess
import json
import tempfile
from typing import Tuple, Any, Callable, Dict, List, Optional, TypedDict
import requests
import argparse

global PROMPTS_DIR
PROMPTS_DIR: str = os.path.join(os.environ.get("HOME"), ".prompts")  # type: ignore
OPENAIKEY: str = os.environ.get("OPENAI_API_KEY")  # type: ignore
CFG_FILENAME = ".hey_config.json"
DEFAULT_CONVO = "main"
DEFAULT_CTX_FILENAME = ".hey_context.main.json"
EDITOR = os.environ.get("EDITOR", "nvim")


class PromptType(TypedDict):
    role: str
    content: str


class ContextType(TypedDict):
    start_date: Optional[str]
    end_date: Optional[str]
    md_file: Optional[str]
    messages: List[PromptType | Any]
    smart_title: Optional[str]
    smart_title_slug: Optional[str]


class ConfigDict(TypedDict):
    model: str
    temp: int
    prompts_dir: str
    editor: str
    pins: List[str]
    convo: str
    context_filename: str


# move to module
class util:
    @staticmethod
    def ctx_path(prompts_dir: str, convo: str):
        return os.path.join(prompts_dir, f".hey_context.{convo}.json")

    @staticmethod
    def uuid(len: int = 8):
        return "".join(random.choices(string.ascii_letters + string.digits, k=len))

    @staticmethod
    def log(*args: Any, **kwargs: Any) -> None:
        if os.environ.get("HEY_OUT") != None:
            print(*args, file=open(os.environ["HEY_OUT"], "w"))
        else:
            print(*args, **kwargs)

    @staticmethod
    def date_block(date: datetime):
        return f"""
## {date.strftime("%Y-%m-%d %H:%M:%S")}
"""

    @staticmethod
    def title_block(title: str):
        return f"""
# {title.strip('"').capitalize()}
              """

    @staticmethod
    def msg_block(prompt: PromptType):
        role = prompt["role"]
        content = prompt["content"]
        return f"""
### {role.capitalize()}
{content}
              """

    @staticmethod
    def log_prompts(user_prompt: PromptType, ai_prompt: PromptType):
        util.log(util.msg_block(user_prompt) + util.msg_block(ai_prompt))

    @staticmethod
    def recent_file(dir: str, ext: str):
        all_files = sorted(
            [os.path.join(dir, f) for f in os.listdir(dir) if f.endswith("." + ext)],
            key=os.path.getmtime,
        )
        return all_files[-1] if len(all_files) > 0 else None

    @staticmethod
    def slugify(string: str, separator: str = "_"):
        string = re.sub(r"[^\w\s-]", "", string).strip().lower()
        string = re.sub(r"\s+", separator, string)
        string = re.sub(r"[^\w\s-]", "", string)
        return string


class Prompt:
    @staticmethod
    def user(content: str) -> PromptType:
        return {
            "role": "user",
            "content": content,
            # "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def ai(content: str) -> PromptType:
        return {
            "role": "assistant",
            "content": content,
            # "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def title(max_char: int = 32) -> PromptType:
        content = (
            "give a title for the previous prompt with a maximum character count of "
            + str(max_char)
        )
        return {
            "role": "user",
            "content": content,
            # "timestamp": datetime.now().isoformat(),
        }


class CLI:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="CLI for model configuration and prompt management."
        )
        parser.add_argument(
            "--no_editor", action="store_true", help="do not open the editor"
        )
        parser.add_argument(
            "--reset", action="store_true", help="reset the context and config"
        )
        parser.add_argument(
            "--qk",
            action="store_true",
            help="quick and dirty mode, one-liner from cli, no editor, does not save prompts, uses gpt-3.5 for speed and cost",
        )

        parser.add_argument(
            "--qk4",
            action="store_true",
            help="gpt4 quick and dirty mode, one-liner from cli, no editor, does not save prompts",
        )
        parser.add_argument(
            "--get_model", action="store_true", help="get the current model"
        )

        parser.add_argument("--delete_convo", type=str, help="delete prompt convo")

        parser.add_argument(
            "--archive", action="store_true", help="move all convos to archive"
        )

        parser.add_argument(
            "--one_shot",
            action="store_true",
            help="one shot gpt4, does not save prompts",
        )

        parser.add_argument(
            "--tidy", action="store_true", help="tidy orphaned contexts"
        )
        parser.add_argument("--pins", action="store_true", help="list all pins")
        parser.add_argument(
            "--pin", action="store_true", help="pin the current context"
        )
        parser.add_argument("--unpin", type=str, help="unpin the given pin")
        parser.add_argument("--models", action="store_true", help="list all models")
        parser.add_argument("--temp", type=int, help="set temperature: 1-10")
        parser.add_argument(
            "--set_model",
            type=str,
            help="set the current model to the nth model in the list",
        )
        parser.add_argument(
            "--dir",
            type=str,
            help="set the prompts directory and subsequent config and context files",
        )
        parser.add_argument(
            "--editor",
            type=str,
            help="set the editor path",
        )
        parser.add_argument("--new_convo", action="store_true", help="new prompt convo")
        parser.add_argument("--set_pin", type=str, help="set prompt convo to pin")
        parser.add_argument("--set_convo", type=str, help="set prompt convo")
        parser.add_argument("--show", type=str, help="show prompt convo")
        parser.add_argument("--convos", action="store_true", help="list convos")
        parser.add_argument(
            "--convos_with_files",
            action="store_true",
            help="list convos with files",
        )
        parser.add_argument(
            "--recent",
            action="store_true",
            help="output the most recent prompt read from the context file",
        )
        parser.add_argument(
            "--info",
            action="store_true",
            help="context, config and prompts directory",
        )
        parser.add_argument(
            "--trim",
            type=int,
            help="trim the first <n> responses from the context when fetching the next prompt",
        )
        parser.add_argument(
            "--new", action="store_true", help="create new conversation / context"
        )
        parser.add_argument(
            "--retry", action="store_true", help="retry the last prompt"
        )
        parser.add_argument("--init", action="store_true", help="init the last prompt")
        parser.add_argument(
            "sentence",
            nargs=argparse.REMAINDER,
            default=None,
            help="Capture remaining input after flags",
        )
        args = parser.parse_args()

        self.get_model = args.get_model
        self.qk = args.qk
        self.new_convo = args.new_convo
        self.models = args.models
        self.retry = args.retry
        self.set_model = args.set_model
        self.show = args.show
        self.convos_with_files = args.convos_with_files
        self.temp = args.temp
        self.set_convo = args.set_convo
        self.set_pin = args.set_pin
        self.reset = args.reset
        self.tidy = args.tidy
        self.unpin = args.unpin
        self.archive = args.archive
        self.recent = args.recent
        self.init = args.init
        self.convos = args.convos
        self.qk4 = args.qk4
        self.openeditor = not args.no_editor
        self.editor = args.editor
        self.pins = args.pins
        self.pin = args.pin
        self.trim = args.trim
        self.delete_convo = args.delete_convo
        self.new = args.new
        self.one_shot = args.one_shot
        self.info = args.info
        self.dir = args.dir
        self.sentence = " ".join(args.sentence) if args.sentence else None


class PropsMixin:
    def __init__(self, obj: Any, filename: str):
        self.obj = obj
        if not filename:
            raise Exception("PropsMixin: error=filename is required")
        self.filename = filename

    def merge(self, other_obj: Dict[str, str]):
        self.obj = {**self.obj, **other_obj}

    def to_json(self):
        return json.dumps(self.obj)

    def from_json(self, json_str: str, merge: bool = True):
        o = json.loads(json_str)
        if merge:
            self.merge(o)
        else:
            self.obj = o

    def save(self):
        with open(self.filename, "w+") as f:
            f.write(self.to_json())

    def open(self):
        with open(self.filename, "r") as f:
            self.from_json(f.read())

    def get_date(self, key: str):
        if self.obj.get(key) is None:
            return None
        if isinstance(self.obj.get(key), str):
            try:
                return datetime.fromisoformat(self.obj[key])
            except ValueError:
                pass

    def gentle_save(self):
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
            self.save()


class Config(PropsMixin):
    def __init__(
        self,
        prompts_dir: str = PROMPTS_DIR,
        filename: str = CFG_FILENAME,
        editor: str = EDITOR,
        convo: str = DEFAULT_CONVO,
        ctx_filename: str = DEFAULT_CTX_FILENAME,
    ):
        obj: ConfigDict = {
            "model": "gpt-3.5-turbo",
            "temp": 7,
            "pins": [],
            "prompts_dir": prompts_dir,
            "editor": editor,
            "convo": convo,
            "context_filename": ctx_filename,
        }
        self.obj = obj
        super().__init__(
            obj,
            os.path.join(prompts_dir, filename),
        )

    def remove_pin(self, pin: str = ""):
        pin = pin or self.obj["convo"]
        if pin in self.obj["pins"]:
            self.obj["pins"].remove(pin)
            self.save()

    def add_pin(self, pin: str = ""):
        pin = pin or self.obj["convo"]
        if pin not in self.obj["pins"]:
            self.obj["pins"].append(pin)
            self.save()

    def list_context_files(self):
        dir: str = self.prompts_dir or PROMPTS_DIR
        all_files = sorted(
            [
                os.path.join(dir, f)
                for f in os.listdir(dir)
                if f.startswith(".hey_context.")
            ],
            key=os.path.getmtime,
            reverse=True,
        )
        return all_files

    def list_convos(self):
        return [f.split(".")[-2] for f in self.list_context_files()]

    @property
    def context_filename(self):
        return self.obj["context_filename"]

    @context_filename.setter
    def context_filename(self, value: str):
        self.obj["context_filename"] = value
        self.save()

    @staticmethod
    def New():
        return Config(
            filename=CFG_FILENAME,
            prompts_dir=PROMPTS_DIR,
            ctx_filename=DEFAULT_CTX_FILENAME,
        )

    @property
    def model(self):
        return self.obj["model"]

    @property
    def convo(self):
        return self.obj["convo"]

    @convo.setter
    def convo(self, value: str):
        self.obj["convo"] = value
        self.save()

    @property
    def temp(self):
        return self.obj["temp"]

    @temp.setter
    def temp(self, value: int):
        self.obj["temp"] = value
        self.save()

    @property
    def editor(self):
        return self.obj["editor"]

    @editor.setter
    def editor(self, value: str):
        self.obj["editor"] = value
        self.save()

    @property
    def pins(self):
        return self.obj["pins"]

    @pins.setter
    def pins(self, value: List[str]):
        self.obj["pins"] = value
        self.save()

    @model.setter
    def model(self, value: str):
        self.obj["model"] = value
        self.save()

    @property
    def prompts_dir(self):
        return self.obj["prompts_dir"]

    @prompts_dir.setter
    def prompts_dir(self, value: str):
        self.obj["prompts_dir"] = value
        self.save()


class Context(PropsMixin):
    def __init__(self, prompts_dir: str = PROMPTS_DIR, convo: str = DEFAULT_CONVO):
        obj: ContextType = {
            "start_date": datetime.now().isoformat(),
            "end_date": None,
            "md_file": None,
            "messages": [],
            "smart_title": None,
            "smart_title_slug": None,
        }
        self.obj = obj
        super().__init__(
            obj,
            util.ctx_path(prompts_dir, convo),
        )

    @staticmethod
    def New(
        prompts_dir: str = PROMPTS_DIR,
        convo: str = DEFAULT_CONVO,
    ):

        return Context(convo=convo, prompts_dir=prompts_dir)

    @property
    def md_file(self):
        return self.obj["md_file"]

    @property
    def smart_title(self):
        return self.obj["smart_title"]

    @property
    def smart_title_slug(self):
        return self.obj["smart_title_slug"]

    @property
    def messages(self):
        return self.obj["messages"]

    @property
    def start_date(self):
        return self.get_date("start_date")

    @start_date.setter
    def start_date(self, value: str | datetime):
        if isinstance(value, datetime):
            value = value.isoformat()
        self.obj["start_date"] = value
        self.save()

    @property
    def end_date(self):
        return self.get_date("end_date")

    @end_date.setter
    def end_date(self, value: str | datetime):
        if isinstance(value, datetime):
            value = value.isoformat()
        self.obj["end_date"] = value
        self.save()

    @md_file.setter
    def md_file(self, value: str):
        self.obj["md_file"] = value
        self.save()

    @messages.setter
    def messages(self, value: List[PromptType | None]):
        self.obj["messages"] = value
        self.save()

    @smart_title.setter
    def smart_title(self, title: str):
        self.obj["smart_title"] = title
        self.save()

    @smart_title_slug.setter
    def smart_title_slug(self, title: str):
        slug = util.slugify(title)
        self.obj["smart_title_slug"] = slug

    def pop_user_prompt(self):
        try:
            if self.obj["messages"][-2]["role"] != "user":
                return None
            self.obj["messages"].pop(-1)
            u = self.obj["messages"].pop(-1)
            return u["content"]
        except:
            return None


class Fetch:
    prompt_temp = 0.7
    prompt_url = "https://api.openai.com/v1/chat/completions"
    engine_url = "https://api.openai.com/v1/engines"

    openaikey: str = OPENAIKEY

    @staticmethod
    def New():
        return Fetch()

    def __init__(self):
        self.headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.openaikey,
        }

    def list_models(self):
        res = requests.get(self.engine_url, headers=self.headers)
        return res.json()

    def models(self):
        res = requests.get(self.engine_url, headers=self.headers)
        return res.json()

    def smart_title(self, ledger: List[PromptType], max_char: int = 32):
        messages: List[PromptType] = ledger + [Prompt.title(max_char)]
        return self.prompt(messages, model="gpt-3.5-turbo")

    def prompt(
        self,
        messages: List[PromptType],
        model: str,
        prompt_temp: float = prompt_temp,
    ):
        text = ""
        json_data: Any = {}
        try:
            data = {
                "model": model,
                "messages": messages,
                "temperature": prompt_temp or self.prompt_temp,
            }
            res = requests.post(
                self.prompt_url,
                headers=self.headers,
                json=data,
            )
            text = res.text
            json_data = res.json()
            return (json_data["choices"][0]["message"]["content"], None)
        except KeyError:
            e = Exception(f"unrecognized response in fetch_prompt: {text}")
            return (json_data, e)
        except json.JSONDecodeError as error:
            e = Exception(f"error parsing response in fetch_prompt: {error}")
            return (text, e)
        except Exception as error:
            return (text, error)


class Client:
    def __init__(
        self,
        fetcher: Fetch = Fetch.New(),
        config: Config = Config.New(),
        context: Context = Context.New(),
    ):
        self.fetcher = fetcher
        self.config = config
        self.context = context
        self.gentle_install()
        self.read_all()

    @staticmethod
    def New(
        fetcher: Fetch = Fetch.New(),
        config: Config = Config.New(),
        context: Context | None = None,
    ):
        if not context:
            context = Context.New(convo=config.convo, prompts_dir=config.prompts_dir)
        return Client(fetcher=fetcher, config=config, context=context)

    def delete_convo(self, convo_id: str, convo_title: str, md_file: str):
        # print(f"Deleting convo {convo_id} {convo_title} {md_file}")
        ans = input(f"Delete convo: {convo_title}? (y/n) ")
        if ans.lower() == "y":
            os.remove(util.ctx_path(self.config.prompts_dir, convo_id))
            os.remove(md_file)

    def tidy_contexts(self):
        for ctx_file in self.config.list_context_files():
            try:
                ctx = json.load(open(ctx_file))
                if ctx.get("smart_title"):
                    continue
            except:
                pass
            os.remove(ctx_file)
            print(f"Removing {ctx_file}")

    @staticmethod
    def set_dir(dir: str):
        Client.set_dir(dir)
        print("setting prompts dir:", dir)
        global PROMPTS_DIR
        PROMPTS_DIR = dir  # type: ignore
        return Client.New().reset(True)

    def pins(self):
        return self.config.pins

    def archive(self):
        archive_dir = os.path.join(self.config.prompts_dir, "archive")
        # self.pins
        # /Users/robertpolana/.prompts/.hey_context.JcTzSesN.json

        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)

        for f in self.config.list_context_files():
            # get basename of f
            fbasename = os.path.basename(f)
            archive_fpath = os.path.join(archive_dir, fbasename)
            # get id from hey_context basename
            id = fbasename.split(".")[2]
            # if id is in self.pins
            if id in self.config.pins:
                print(f"{f} is pinned, skipping")
                continue
            print(f"archiving {fbasename}")
            os.rename(f, archive_fpath)
        return

    def info(self):
        print("prompts dir:", self.config.prompts_dir)
        print("config file:", self.config.filename)
        print("context file:", self.context.filename)
        print("editor:", self.config.editor)
        print("model:", self.config.model)
        print("md_file:", self.context.md_file)
        print("temp:", self.config.temp / 10)
        print("convo:", self.config.convo)
        if self.context.smart_title:
            print("smart_title:", self.context.smart_title)
        print("messages:", len(self.context.messages))

    def get_convos(self):
        return self.config.list_convos()

    def convos_with_titles(self):
        return self.add_titles_to_convos(self.config.list_convos())

    def add_titles_to_convos(self, convos: List[str]):
        convos = convos
        convos_with_titles: List[Tuple[str, str, str]] = []
        for _, b in enumerate(convos):
            b_path = util.ctx_path(self.config.prompts_dir, b)
            title: str = "unknown"
            mdfile: str = ""
            if os.path.exists(b_path):
                with open(b_path, "r") as f:
                    j = json.load(f)
                    title = j["smart_title"]
                    mdfile = j["md_file"]
            convos_with_titles.append((b, title, mdfile))
        return convos_with_titles

    def print_pins_with_titles(self):
        if not self.config.pins:
            return print("no pins")
        self.print_convoe_title_enumeration(
            convos_with_titles=self.add_titles_to_convos(self.config.pins)
        )

    def print_convos_with_title_and_files(self):
        return self.print_convoe_title_enumeration(
            convos_with_titles=self.add_titles_to_convos(self.get_convos()),
            with_filename=True,
        )

    def print_convos_with_title(self):
        return self.print_convoe_title_enumeration(
            convos_with_titles=self.add_titles_to_convos(self.get_convos())
        )

    def print_convoe_title_enumeration(
        self,
        convos_with_titles: List[Tuple[str, str, str]],
        with_filename: bool = False,
    ):
        for i, (b, title, filename) in enumerate(convos_with_titles):
            f = f" @{filename}" if with_filename else ""
            if not title:
                title = "<BLANK>"
            if self.convo != b:
                # not printing convo id
                print(f"{i}: {title}{f}")
            else:
                # not printing convo id
                print(f"\033[1m{i}: {title}\033[0m")

    def add_prompts(self, user_prompt: PromptType, ai_prompt: PromptType):
        self.add_prompt(user_prompt)
        self.add_prompt(ai_prompt)
        slug = self.check_and_set_smart_title()
        if not self.context.md_file:
            self.context.md_file = self.mk_prompt_path(slug)
        self.context.end_date = datetime.now()
        if not self.context.start_date:
            self.context.start_date = datetime.now().isoformat()
        if not os.path.exists(self.context.md_file):
            self.write_header()
        self.write_conversation()

    # conveniece method for adding a single prompt to the context
    def fetch_prompt_with_context(self, prompt: str, trim: int = 0, model: str = ""):
        user_prompt = Prompt.user(prompt)
        ctx = (self.context.messages + [user_prompt])[trim:]
        return self.fetch_prompt(ctx, model=(model or self.model))

    def fetch_prompt(self, messages: List[PromptType], model: str = ""):
        response, error = self.fetcher.prompt(
            messages, model or self.model, self.config.temp / 10
        )
        if error:
            print("error fetch_prompt=" + str(error))
            raise Exception(str(error) + "\n" + str(response))
        return Prompt.ai(str(response))

    def reset(self, silent: bool = False):
        self.context = Context.New()
        self.config = Config.New()
        if not silent:
            print("set context and config")
            self.info()
        self.write_all()

    def add_pin(self):
        self.config.add_pin()
        return print("pin added")

    def remove_pin(self, pin: str):
        self.config.remove_pin(pin)

    @property
    def convo(self):
        return self.config.convo

    @convo.setter
    def convo(self, value: str):
        self.config.convo = value

    @property
    def model(self):
        return self.config.model

    @model.setter
    def model(self, value: str):
        self.config.model = value

    @property
    def editor(self):
        return self.config.editor

    def pop_user_prompt(self):
        return self.context.pop_user_prompt()

    def load_context(self, convo: str):
        return self.new_context(convo)

    def new_context(self, convo: str = util.uuid()):
        self.config.convo = convo
        self.context = Context.New(convo=self.config.convo)
        self.context.save()
        self.config.context_filename = self.context.filename
        self.config.save()

    def most_recent_convo(self, force_recent: bool = True):
        f: str | None = self.context.md_file
        if force_recent and (not f or not os.path.exists(f)):
            f = util.recent_file(self.config.prompts_dir, "md")
        if f:
            with open(f, "r") as md_file:
                return md_file.read()

    def mk_prompt_path(self, slug: str):
        if not os.path.exists(os.path.join(self.config.prompts_dir, slug + ".md")):
            return os.path.join(self.config.prompts_dir, slug + ".md")
        id = 0
        while True:
            filename = os.path.join(
                self.config.prompts_dir, f"{slug}_{id}.md".replace("_+", "_")
            )
            if not os.path.exists(filename):
                return filename
            id += 1

    def write_header(self):
        if (
            self.context.md_file
            and self.context.smart_title
            and self.context.start_date
        ):
            with open(self.context.md_file, "a+") as f:
                f.write(util.title_block(self.context.smart_title))
                f.write(util.date_block(self.context.start_date))

    def write_conversation(self):
        if self.context.md_file and self.context.messages:
            with open(self.context.md_file, "a+") as f:
                for message in self.context.messages:
                    f.write(util.msg_block(message))
        else:
            raise Exception("no context.md_file or context.messages")

    def add_prompt(self, message: PromptType):
        self.context.messages.copy()
        self.context.messages.extend([message])

    def gentle_install(self):
        if not os.path.exists(self.config.prompts_dir):
            os.mkdir(self.config.prompts_dir)
        self.context.gentle_save()
        self.config.gentle_save()

    def read_all(self):
        self.context.open()
        self.config.open()

    def write_all(self):
        self.context.save()
        self.config.save()

    def check_and_set_smart_title(
        self,
    ):
        if len(self.context.messages) == 2 or not self.context.smart_title:
            self.context.smart_title = self.conjure_smart_title(64).strip('"')
            self.context.smart_title_slug = util.slugify(self.context.smart_title)

        return self.context.smart_title_slug or ""

    def conjure_smart_title(self, max_length: int = 32):
        msgs = self.context.messages
        fallbackname = (
            msgs[-1]["content"][:max_length]
            if len(msgs) > 0
            else datetime.now().strftime("%Y-%m-%d")
        )
        (title, error) = self.fetcher.smart_title(msgs, max_length)
        if error:
            print(error)
            return fallbackname
        else:
            print(">", str(title))
            return str(title)


class Interactive:
    def __init__(self, client: Client, fetcher: Fetch):
        self.fetcher = fetcher
        self.client = client

    @staticmethod
    def New(client: Client = Client.New(), fetcher: Fetch = Fetch.New()):
        return Interactive(client=client, fetcher=fetcher)

    def make_new(self):
        if self.client.context.end_date is not None:
            print("new context/convo created")
            self.client.new_context()
        else:
            print(self.client.context.filename)

    def set_editor(self, editor: str):
        c = Config.New()
        c.open()
        c.editor = editor
        return print("set editor to", editor)

    def set_temp(self, temp: int):
        if temp >= 0 and temp <= 10:
            self.client.config.temp = temp
            print("temp set to:", temp)
        else:
            print("invalid temp, must be between 0 and 10")

    def check_fresh_context(self):
        if self.should_date_make_new():
            self.client.new_context()

    def should_date_make_new(self):
        end_date = self.client.context.end_date or datetime.now()
        cur_date = datetime.now()
        two_hours = timedelta(hours=2)
        if cur_date - end_date > two_hours:
            ans = input("Context is older than 2hrs, create a new one? (y/n) ")
            return ans.lower() == "y"
        return False

    def show_context(self, index_or_name: str):
        bs = self.client.convos_with_titles()
        convo_titles = [str(title) for _, title, __ in bs]

        def output_md_file(idx: int):
            convo = bs[idx][0]
            ctx_file = util.ctx_path(self.client.config.prompts_dir, convo)
            md_file = json.load(open(ctx_file))["md_file"]
            with open(md_file, "r") as mdf:
                util.log(mdf.read())

        self.pick_list(
            convo_titles,
            index_or_name,
            output_md_file,
            "convo",
        )

    def set_convo(self, index_or_name: str):
        bs = self.client.convos_with_titles()
        convo_titles = [str(title) for _, title, __ in bs]
        return self.pick_list(
            convo_titles,
            index_or_name,
            lambda idx: setattr(self.client, "convo", bs[idx][0]),
            "convo",
        )

    def delete_convo(self, index_or_name: str):
        bs = self.client.convos_with_titles()
        convo_titles = [str(title) for _, title, __ in bs]
        return self.pick_list(
            convo_titles,
            index_or_name,
            lambda idx: self.client.delete_convo(*bs[idx]),
            "convo",
            "delete",
        )

    def set_pin(self, index_or_name: str):
        bs = self.client.add_titles_to_convos(convos=self.client.config.pins)
        convo_titles = [str(title) for _, title, __ in bs]
        return self.pick_list(
            convo_titles,
            index_or_name,
            lambda idx: setattr(self.client, "convo", bs[idx][0]),
            "pin",
        )

    def unset_pin(self, index_or_name: str):
        bs = self.client.add_titles_to_convos(convos=self.client.config.pins)
        convo_titles = [str(title) for _, title, __ in bs]
        return self.pick_list(
            convo_titles,
            index_or_name,
            lambda idx: self.client.remove_pin(bs[idx][0]),
            "pin",
            "unset",
        )

    def set_model(self, index_or_name: str):
        models = self.get_list()
        self.pick_list(
            models,
            index_or_name,
            lambda idx: setattr(self.client, "model", models[idx]),
            "model",
        )

    def pin(self):
        self.client.add_pin()

    def pick_list(
        self,
        ls: List[str],
        index_or_name: str,
        setter: Callable[[int], None],
        name: str = "list",
        action: str = "set",
    ):
        if index_or_name.isdigit():
            index = int(index_or_name)
            try:
                setter(index)
            except IndexError:
                return print(f"invalid {name} index, try again")
            print(f"{name} {action}: {ls[index]}")
        else:
            if index_or_name not in ls:
                closest = difflib.get_close_matches(index_or_name, ls, n=1)
                closest_start_match = [
                    match for match in ls if match.startswith(index_or_name)
                ]
                if len(closest) > 0:
                    index_or_name = closest[0]
                elif len(closest_start_match) > 0:
                    index_or_name = closest_start_match[0]
                else:
                    return print("no close matches found")
            index = ls.index(index_or_name)
            setter(index)
            print(f"\n{name} set:\n\t {ls[index]}")

    def get_list(self):
        res = self.fetcher.list_models()
        return [d["id"] for d in res["data"] if d["id"].startswith("gpt")]

    def num_list(self):
        models = self.get_list()
        for i, model in enumerate(models):
            if self.client.model != model:
                print(f"{i}:{model}")
            else:
                print(f"\033[1m{i}:{model}\033[0m")

    def author_prompt(self, content: str = "", is_retry: bool = False):
        if is_retry:
            content = self.client.pop_user_prompt() or ""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            file = f.name
            with open(file, "w") as f:
                f.write(content)
            editor: str = self.client.editor
            subprocess.run([editor, file], check=True)
            with open(file, "r") as f:
                pmpt = f.read().strip()
                return pmpt if pmpt != "" else None

    def one_shot_prompt(self, content: str = "", open_editor: bool = True):
        p = self.author_prompt(content) if open_editor else content
        if open_editor:
            print(p)
        return self.qk_prompt4(sentence=p)

    def qk_prompt4(self, sentence: str | None):
        return self.qk_prompt(sentence, model="gpt-4")

    def qk_prompt(self, sentence: str | None, model: str = "gpt-3.5-turbo"):
        if not sentence:
            return print("no sentence given")
        else:
            return util.log(
                self.client.fetch_prompt([Prompt.user(sentence)], model=model)[
                    "content"
                ]
            )

    def do_prompt(
        self,
        content: str = "",
        open_editor: bool = True,
        trim: int = 0,
        is_retry: bool = False,
    ):
        prompt: str = ""
        try:
            prompt = (
                (self.author_prompt(content, is_retry) or "")
                if open_editor
                else content
            )
            if not prompt:
                return print("no prompt given")
            print(prompt)
            user_prompt = Prompt.user(prompt)

            ai_prompt = self.client.fetch_prompt_with_context(prompt=prompt, trim=trim)
            self.client.add_prompts(user_prompt, ai_prompt)
            util.log_prompts(user_prompt, ai_prompt)
        except Exception as e:
            self.client.add_prompt(Prompt().user(prompt))
            self.client.add_prompt(Prompt().ai("Error:" + str(e)))
            self.client.write_all()
            print(e)


def main():

    global PROMPTS_DIR
    myclient = Client.New()
    myinteractive: Interactive = Interactive.New(client=myclient)
    myCLI = CLI()
    trim = myCLI.trim or 0
    if myCLI.set_convo:
        return myinteractive.set_convo(myCLI.set_convo)

    if myCLI.set_pin:
        return myinteractive.set_pin(myCLI.set_pin)

    if myCLI.convos_with_files:
        return myclient.print_convos_with_title_and_files()
    if myCLI.convos:
        return myclient.print_convos_with_title()

    if myCLI.temp is not None:
        return myinteractive.set_temp(myCLI.temp)

    if myCLI.tidy:
        return myclient.tidy_contexts()

    if myCLI.show is not None:
        return myinteractive.show_context(myCLI.show)

    if myCLI.pin:
        return myclient.add_pin()

    if myCLI.pins:
        return myclient.print_pins_with_titles()

    if myCLI.unpin is not None:
        # return print(myCLI.unpin)
        return myinteractive.unset_pin(myCLI.unpin)

    if myCLI.init:
        PROMPTS_DIR = os.getcwd()  # type: ignore
        return Client.New().reset()
    if myCLI.dir:
        return Client.set_dir(myCLI.dir)

    if myCLI.one_shot:
        return myinteractive.one_shot_prompt(
            content=myCLI.sentence or "", open_editor=myCLI.openeditor
        )

    if myCLI.delete_convo:
        return myinteractive.delete_convo(myCLI.delete_convo)
    if myCLI.archive:
        return myclient.archive()
    if myCLI.qk:
        return myinteractive.qk_prompt(myCLI.sentence)
    if myCLI.qk4:
        return myinteractive.qk_prompt4(myCLI.sentence)
    if myCLI.new or myCLI.new_convo:
        return myinteractive.make_new()
    if myCLI.models:
        return myinteractive.num_list()
    if myCLI.set_model != None:
        return myinteractive.set_model(myCLI.set_model)
    if myCLI.get_model:
        return print(myclient.model)
    if myCLI.recent:
        return util.log(myclient.most_recent_convo())
    if myCLI.sentence:
        # disable for now: myinteractive.check_fresh_context()
        return myinteractive.do_prompt(
            content=myCLI.sentence, trim=trim, open_editor=myCLI.openeditor
        )
    if myCLI.retry:
        return myinteractive.do_prompt(is_retry=True, trim=trim)
    if myCLI.reset:
        return myclient.reset()
    if myCLI.new:
        return myclient.new_context()
    if myCLI.info:
        return myclient.info()

    if myCLI.editor:
        return myinteractive.set_editor(myCLI.editor)

    # disable for now: myinteractive.check_fresh_context()
    return myinteractive.do_prompt(content="", trim=trim)


if __name__ == "__main__":
    main()